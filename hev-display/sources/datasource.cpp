// © Copyright CERN, Riga Technical University and University of Liverpool 2020.
// All rights not expressly granted are reserved. 
// 
// This file is part of hev-sw.
// 
// hev-sw is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public Licence as published by the Free
// Software Foundation, either version 3 of the Licence, or (at your option)
// any later version.
// 
// hev-sw is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public Licence
// for more details.
// 
// You should have received a copy of the GNU General Public License along
// with hev-sw. If not, see <http://www.gnu.org/licenses/>.
// 
// The authors would like to acknowledge the much appreciated support
// of all those involved with the High Energy Ventilator project
// (https://hev.web.cern.ch/).


#include "datasource.h"

#include <chrono>
#include <QtCharts/QXYSeries>
#include <QtCharts/QValueAxis>
#include <QtConcurrent>
#include <QtCore/QDebug>
#include <QtCore/QJsonArray>
#include <QtCore/QJsonObject>
#include <QtCore/QRegularExpression>
#include <QtCore/QScopedPointer>
#include <QtCore/QtMath>
#include <QMutexLocker>

using namespace std::chrono;
QT_CHARTS_USE_NAMESPACE

Q_DECLARE_METATYPE(QAbstractSeries *)
Q_DECLARE_METATYPE(QAbstractAxis *)

static const int MAX_SECONDS = 60;
static const int TARGET_FPS = 25;
static const qreal DEFAULT_AXIS_LIMIT = std::numeric_limits<qint64>::min();

static void addSample(DataSet &set, DataAxis &axis, qreal sample, qint64 ms, bool clearAll=false)
{
  QMutexLocker setLock(set.mutex);

  auto &points = set.points;

  qreal y_axis_min = qMin(0., sample);
  qreal y_axis_max = qMax(0., sample);

  for (auto it = points.begin(); it != points.end(); ++it) {
    it->setX(it->x() - ms * 0.001);
    if (clearAll || (abs(ceil(it->x())) > MAX_SECONDS)) {
      points.erase(it, points.end());
      break;
    }

    qreal y = it->y();
    if (y < y_axis_min) {
      y_axis_min = y;
    }
    if (y > y_axis_max) {
      y_axis_max = y;
    }
  }

  points.insert(0, QPointF(0, sample));

  QMutexLocker axisLock(axis.mutex);
  if (set.series && set.visible) {
    if ((axis.minOrig == DEFAULT_AXIS_LIMIT) || (y_axis_min < axis.minOrig)) {
      axis.minOrig = y_axis_min;
    }
    if ((axis.maxOrig == DEFAULT_AXIS_LIMIT) || (y_axis_max > axis.maxOrig)) {
      axis.maxOrig = y_axis_max;
    }
  }
  set.dirty = true;
}

AlarmObject::AlarmObject(QString message, QString priority, QDateTime since, QObject *parent)
: QObject(parent)
, _priority(priority)
, _message(message)
, _since(since)
, _until(_since)
{}

BroadcastReceiver::BroadcastReceiver(QString host, quint16 port, DataSource &source, QObject *parent)
: QObject(parent)
, _host(host)
, _port(port)
, _source(source)
{
  qRegisterMetaType<QAbstractSocket::SocketError>();

  connect(&_sock, &QAbstractSocket::connected, this, &BroadcastReceiver::connected);
  connect(&_sock, &QAbstractSocket::disconnected, this, &BroadcastReceiver::disconnected);
  connect(&_sock, QOverload<QAbstractSocket::SocketError>::of(&QAbstractSocket::error), this, &BroadcastReceiver::error);
  connect(&_sock, &QIODevice::readyRead, this, &BroadcastReceiver::receive);
}

void BroadcastReceiver::connectToServer()
{
  if (_sock.state() == QAbstractSocket::UnconnectedState) {
    qDebug() << "Socket is disconnected, trying to reconnect";
    _sock.connectToHost(_host, _port);
  }
}

void BroadcastReceiver::disconnectFromServer()
{
  _sock.abort();
}

void BroadcastReceiver::receive()
{
  _source.pushBuffer(_sock.readAll());
}

BroadcastParser::BroadcastParser(DataSets &sets, DataAxes &axes, DataSource &source, QObject *parent)
: QThread(parent)
, _source(source)
, _sets(sets)
, _axes(axes)
{}

void BroadcastParser::run()
{
  while (_parsing) {
    QByteArray buffer(_source.popBuffer());
    if (buffer.isEmpty()) {
      break;
    }

    for (auto &axis : _axes) {
      QMutexLocker axisLock(axis.mutex);
      if ((axis.minOrig != DEFAULT_AXIS_LIMIT) && ((axis.min > axis.minOrig) || (axis.min < axis.minOrig * 0.8))) {
        axis.min = axis.minOrig * 1.1;
        axis.dirty = true;
      }
      if ((axis.maxOrig != DEFAULT_AXIS_LIMIT) && ((axis.max < axis.maxOrig) || (axis.max * 0.8 > axis.maxOrig))) {
        axis.max = axis.maxOrig * 1.1;
        axis.dirty = true;
      }
      axis.minOrig = DEFAULT_AXIS_LIMIT;
      axis.maxOrig = DEFAULT_AXIS_LIMIT;
    }

    QJsonDocument document = QJsonDocument::fromJson(buffer);
    if (document.isNull()) {
      qDebug() << "ERROR: Got invalid document";
      qDebug() << buffer;
      continue;
    }
    QJsonObject json = document.object();
    QString type = document["type"].toString();
    if (type == "keepalive") {
      // Do nothing
      continue;
    } else if (type == "DEBUG") {
      // Do nothing
    } else if (type == "CMD") {
        QJsonObject items = json["CMD"].toObject();
        QVariantMap map;
        QVariantMap map2;
        map2.insert(items["cmd_code"].toString(), items["param"].toVariant());
        map.insert(items["cmd_type"].toString(), map2);
        _source.setCmdReadback(map);
    } else if (type == "PERSONAL") {
        QJsonObject items = json["PERSONAL"].toObject();
        for (auto it = items.constBegin(); it != items.constEnd(); ++it) {
          emit _source.personalChanged(it.key(), it.value().toVariant());
        }
    } else if (type == "BATTERY") {
        QJsonObject items = json["BATTERY"].toObject();
        for (auto it = items.constBegin(); it != items.constEnd(); ++it) {
          emit _source.batteryChanged(it.key(), it.value().toVariant());
        }
    } else if (type == "TARGET") {
        QJsonObject items = json["TARGET"].toObject();
        for (auto it = items.constBegin(); it != items.constEnd(); ++it) {
          emit _source.targetChanged(items["mode"].toString(), it.key(), it.value().toVariant());
        }
    }
    else if (type == "IVT") {
      QJsonObject items = json["IVT"].toObject();
      for (auto it = items.constBegin(); it != items.constEnd(); ++it) {
        emit _source.ivtChanged(it.key(), it.value().toVariant());
      }
    } else if (type == "READBACK") {
      QJsonObject items = json["READBACK"].toObject();
      for (auto it = items.constBegin(); it != items.constEnd(); ++it) {
        emit _source.readbackChanged(it.key(), it.value().toVariant());
      }
    } else if (type == "CYCLE") {
      QJsonObject items = json["CYCLE"].toObject();
      for (auto it = items.constBegin(); it != items.constEnd(); ++it) {
        emit _source.cycleChanged(it.key(), it.value().toVariant());
      }
    } else if (type == "DATA") {
      QJsonObject items = json["DATA"].toObject();
      for (auto it = items.constBegin(); it != items.constEnd(); ++it) {
        emit _source.dataChanged(it.key(), it.value().toVariant());
      }
      auto start = high_resolution_clock::now();
      parseData(json);
      auto stop = high_resolution_clock::now();
      auto duration = duration_cast<microseconds>(stop - start);
      if (duration.count() > 20000) {
        qDebug() << "WARNING: Parsing data took longer than budgeted" << duration.count() << "us";
      }
    } else if (type == "ALARM") {
        parseAlarm(json);
    } else {
      qDebug() << "WARNING: Skipping unrecognised type" << type;
      qDebug() << buffer;
    }
    parseActiveAlarms(json);
  }
}

void BroadcastParser::parseData(QJsonObject &json)
{
  QJsonObject data = json["DATA"].toObject();
  QJsonValue timestamp = data["timestamp"];
  // Timestamp must be treated as a double as it is a uint32 on the
  // microcontroller and Qt can only handle int32 for a JSON int
  if (!timestamp.isDouble()) {
    qDebug() << "Error: timestamp has not been parsed as an int" << timestamp;
    return;
  }

  qint64 timestampCurrent = qRound64(timestamp.toDouble());
  const qint64 MAX_JUMP_BACK_WINDOW_MS = 1000;
  bool clearAll = false;
  if ((timestampCurrent >= std::pow(2, 32) - MAX_JUMP_BACK_WINDOW_MS) && (_timestampPrevious < MAX_JUMP_BACK_WINDOW_MS)) {
    timestampCurrent -= std::pow(2, 32);
  }
  if (timestampCurrent < _timestampPrevious) {
    qDebug() << "Recieved out of order data ("
              << "previous timestamp =" << _timestampPrevious
              << "current timestamp =" << timestampCurrent << ")";
    if (_timestampPrevious >= std::pow(2, 32) - MAX_JUMP_BACK_WINDOW_MS) {
      qDebug() << "Detected integer overflow, wrapping...";
      _timestampPrevious -= std::pow(2, 32);
    } else if ((timestampCurrent == 0) || (_timestampPrevious - timestampCurrent) > MAX_JUMP_BACK_WINDOW_MS) {
      qDebug() << "    Discarding out of order data";
      qDebug() << "    More than 1 second behind, assuming clock has reset";
      clearAll = true;
    } else {
      return;
    }
  }

  if (_timestampPrevious == std::numeric_limits<qint64>::min()) {
    qDebug() << "_timestampPrevious is zero, setting to" << timestampCurrent << "and skipping";
    _timestampPrevious = timestampCurrent;
    return;
  }

  qint64 ms = (timestampCurrent - _timestampPrevious);
  // qDebug() << "Time difference between now and the last point is =" << timestampCurrent << _timestampPrevious << ms;

  auto keys = data.keys();
  QtConcurrent::blockingMap(keys, [&](const QString &key) {
    auto value = data[key];
    if (key == "version") {
      // not shown atm
    } else if (key == "fsm_state") {
      //do nothing
    } else if (key == "timestamp") {
    } else {
      // Adding a new element to _sets isn't threadsafe so aquire a lock if
      // in case key doesn't already exist
      if (!_sets.contains(key)) {
        _setsMutex.lock();
        DataSet &set = _sets[key];
        _setsMutex.unlock();
      }
      DataSet &set = _sets[key];
      DataAxis &yAxis = _axes[set.axisName];
      addSample(set, yAxis, value.toDouble(), ms, clearAll);
    }
  });
  _timestampPrevious = timestampCurrent;
}

void BroadcastParser::parseAlarm(QJsonObject &json)
{
  QJsonObject object = json["ALARM"].toObject();
  QString priority = object["alarm_type"].toString();
  QString message  = object["alarm_code"].toString();
  emit alarm(message, priority);
}

void BroadcastParser::parseActiveAlarms(QJsonObject &json)
{
  QJsonArray items = json["alarms"].toArray();
  int count = 0;
  for (auto it = items.constBegin(); it != items.constEnd(); ++it) {
    QJsonObject object = (*it).toObject();
    QString priority = object["alarm_type"].toString();
    QString message  = object["alarm_code"].toString();
    emit alarmActive(message, priority);
    count++;
  }
  if (count == 0) {
    emit alarmActive("","");
  }
}


CommandObject::CommandObject(QString name, QString host, quint16 port, QJsonDocument json, QObject *parent)
: QObject(parent)
, _name(name)
, _json(json)
, _acked(false)
{
  connect(&_sock, &QAbstractSocket::connected, this, &CommandObject::connected);
  connect(&_sock, &QAbstractSocket::disconnected, this, &CommandObject::disconnected);

  // TODO: a command should timeout at some point

  _sock.connectToHost(host, port);
}

void CommandObject::connected()
{
  connect(&_sock, &QAbstractSocket::readyRead, this, &CommandObject::replied);

  QByteArray data = _json.toJson(QJsonDocument::Compact);
  data.append('\0');

  _sock.write(data);

  emit sent(_name);
}

void CommandObject::disconnected()
{
  if (_acked) {
    emit acked(_name);
  } else {
    emit failed(_name);
  }
}

void CommandObject::replied()
{
  _buffer.append(_sock.readAll());

  int len = _buffer.indexOf('\0');
  if (len < 0) {
    return;
  }
  _buffer.truncate(len);

  QJsonDocument document = QJsonDocument::fromJson(_buffer);
  QJsonObject json = document.object();

  if (json["type"].toString() == "ack") {
    _acked = true;
  }
  _sock.disconnectFromHost();
}

DataSource::DataSource(QString host, quint16 port, QObject *parent)
: QObject(parent)
, _host(host)
, _port(port)
, _broadcastReceiver(host, port, *this)
, _broadcastParser(_sets, _axes, *this)
{
  setupReadback();
  setupData();
  setupCycle();
  setupIvt();
  setupTargets();
  setupBattery();
  setupPersonal();
  setupCommandReadback();

  qRegisterMetaType<QAbstractSeries *>();
  qRegisterMetaType<QAbstractAxis *>();

  _broadcastReceiverThread.setObjectName("BroadcastReceiver");
  _broadcastReceiver.moveToThread(&_broadcastReceiverThread);
  _broadcastParser.setObjectName("BroadcastParser");

  connect(&_updateTimer, &QTimer::timeout, this, &DataSource::update);
  connect(&_reconnectTimer, &QTimer::timeout, this, &DataSource::broadcastConnect);
  connect(&_broadcastReceiver, &BroadcastReceiver::connected, this, &DataSource::broadcastConnected);
  connect(&_broadcastReceiver, &BroadcastReceiver::disconnected, this, &DataSource::broadcastDisconnected);
  connect(&_broadcastReceiver, &BroadcastReceiver::error, this, &DataSource::broadcastError);
  connect(&_broadcastParser, &BroadcastParser::alarm, this, &DataSource::raiseAlarm);
  connect(&_broadcastParser, &BroadcastParser::alarmActive, this, &DataSource::statusAlarm);
}

DataSource::~DataSource()
{
  _updateTimer.stop();

  _broadcastReceiverThread.quit();
  _broadcastReceiverThread.wait();
  _broadcastReceiver.deleteLater();

  _broadcastParser.finish(); // NOTE: maybe emit signal instead of the direct call?
  _broadcastParser.wait(1000);
  _buffersNotEmpty.wakeAll();
  _broadcastParser.deleteLater();

  for (auto &set : _sets) {
    delete set.mutex;
  }
  for (auto &axis : _axes) {
    delete axis.mutex;
  }
  auto alarms = _alarms;
  _alarms.clear();
  emit alarmsChanged();
  for (auto &alarm : alarms) {
    delete alarm;
  }
}

static QAbstractSeries *findSeries(QObject *object, QString chartName, QString seriesName)
{
  QObject *chartObject = object->findChild<QObject *>(chartName);
  if (chartObject) {
    int count = chartObject->property("count").toInt();
    for (int i = 0; i < count; ++i) {
      QAbstractSeries *series;
      QMetaObject::invokeMethod(
       chartObject, "series", Qt::AutoConnection, Q_RETURN_ARG(QAbstractSeries *, series), Q_ARG(int, i));
      QString objName = series->objectName();
      if (objName == seriesName) {
        return series;
      }
    }
  }
  return nullptr;
}

void DataSource::setup(QObject *mainWindow)
{
  reset();

  setupChart(mainWindow, "pressureChart");
  setupChart(mainWindow, "flowChart");
  setupChart(mainWindow, "volumeChart");

  //setupChart(mainWindow, "labPressureChart");
  //setupChart(mainWindow, "labFlowChart");
  //setupChart(mainWindow, "labVolumeChart");

  QAbstractSeries *mainPressure = findSeries(mainWindow, "mainPressureChart", "pressure_patient");
  if (mainPressure) {
    _sets["pressure_patient"].mainSeries = mainPressure;
  }
  QAbstractSeries *mainFlow = findSeries(mainWindow, "mainFlowChart", "flow");
  if (mainFlow){
    _sets["flow"].mainSeries = mainFlow;
  }
  QAbstractSeries *mainVolume = findSeries(mainWindow, "mainVolumeChart", "volume");
  if (mainVolume) {
    _sets["volume"].mainSeries = mainVolume;
  }
  _sets["flow"].autoscale = false;

  _updateTimer.setTimerType(Qt::PreciseTimer);
  _updateTimer.start(1000.0/TARGET_FPS);
  //_scrollTimer.restart();

  _broadcastReceiverThread.start();
  _broadcastParser.start();
  broadcastConnect();
}

void DataSource::setupProperty(QQmlPropertyMap &property)
{
  property.insert(""            , QVariant(0));
  property.insert("version"     , QVariant(0));
  property.insert("timestamp"   , QVariant(0));
  property.insert("payload_type", QVariant(0));
}

void DataSource::setupReadback()
{
  setupProperty(_readback);

  _readback.insert("duration_calibration"    , QVariant(0));
  _readback.insert("duration_buff_purge"     , QVariant(0));
  _readback.insert("duration_buff_flush"     , QVariant(0));
  _readback.insert("duration_buff_prefill"   , QVariant(0));
  _readback.insert("duration_buff_fill"      , QVariant(0));
  _readback.insert("duration_buff_pre_inhale", QVariant(0));
  _readback.insert("duration_inhale"         , QVariant(0));
  _readback.insert("duration_pause"          , QVariant(0));
  _readback.insert("duration_exhale_fill"    , QVariant(0));
  _readback.insert("duration_exhale"         , QVariant(0));

  _readback.insert("valve_air_in"            , QVariant(0));
  _readback.insert("valve_o2_in"             , QVariant(0));
  _readback.insert("valve_inhale"            , QVariant(0));
  _readback.insert("valve_exhale"            , QVariant(0));
  _readback.insert("valve_purge"             , QVariant(0));
  _readback.insert("ventilation_mode"        , QVariant("UNKNOWN"));
  _readback.insert("valve_inhale_percent"    , QVariant(0));
  _readback.insert("valve_exhale_percent"    , QVariant(0));
  _readback.insert("valve_air_in_enable"     , QVariant(0));
  _readback.insert("valve_o2_in_enable"      , QVariant(0));
  _readback.insert("valve_purge_enable"      , QVariant(0));
  _readback.insert("inhale_trigger_enable"   , QVariant(0));
  _readback.insert("exhale_trigger_enable"   , QVariant(0));
  _readback.insert("peep"                    , QVariant(0));
  _readback.insert("inhale_exhale_ratio"     , QVariant(0));

  _readback.insert("kp"                      , QVariant(0));
  _readback.insert("ki"                      , QVariant(0));
  _readback.insert("kd"                      , QVariant(0));
  _readback.insert("pid_gain"                , QVariant(0));
  _readback.insert("max_patient_pressure"    , QVariant(0));
}

void DataSource::setupData()
{
  setupProperty(_data);

  _data.insert("fsm_state"              , QVariant(0));
  _data.insert("pressure_air_supply"    , QVariant(0));
  _data.insert("pressure_air_regulated" , QVariant(0));
  _data.insert("pressure_o2_supply"     , QVariant(0));
  _data.insert("pressure_o2_regulated"  , QVariant(0));
  _data.insert("pressure_buffer"        , QVariant(0));
  _data.insert("pressure_inhale"        , QVariant(0));
  _data.insert("pressure_patient"       , QVariant(0));
  _data.insert("temperature_buffer"     , QVariant(0));
  _data.insert("pressure_diff_patient"  , QVariant(0));
  _data.insert("ambient_pressure"       , QVariant(0));
  _data.insert("ambient_temperature"    , QVariant(0));
  _data.insert("airway_pressure"        , QVariant(0));
  _data.insert("flow"                   , QVariant(0));
  _data.insert("volume"                 , QVariant(0));
}

void DataSource::setupCycle()
{
  setupProperty(_cycle);

  _cycle.insert("respiratory_rate"         , QVariant(0));
  _cycle.insert("tidal_volume"             , QVariant(0));
  _cycle.insert("exhaled_tidal_volume"     , QVariant(0));
  _cycle.insert("inhaled_tidal_volume"     , QVariant(0));
  _cycle.insert("minute_volume"            , QVariant(0));
  _cycle.insert("exhaled_minute_volume"    , QVariant(0));
  _cycle.insert("inhaled_minute_volume"    , QVariant(0));
  _cycle.insert("lung_compliance"          , QVariant(0));
  _cycle.insert("static_compliance"        , QVariant(0));
  _cycle.insert("inhalation_pressure"      , QVariant(0));
  _cycle.insert("peak_inspiratory_pressure", QVariant(0));
  _cycle.insert("plateau_pressure"         , QVariant(0));
  _cycle.insert("mean_airway_pressure"     , QVariant(0));
  _cycle.insert("fiO2_percent"             , QVariant(0));
  _cycle.insert("apnea_index"              , QVariant(0));
  _cycle.insert("apnea_time"               , QVariant(0));
  _cycle.insert("mandatory_breath"         , QVariant(0));
}

void DataSource::setupIvt()
{
  setupProperty(_ivt);

  _ivt.insert("inhale_current", QVariant(0));
  _ivt.insert("exhale_current", QVariant(0));
  _ivt.insert("purge_current" , QVariant(0));
  _ivt.insert("air_in_current", QVariant(0));
  _ivt.insert("o2_in_current" , QVariant(0));
  _ivt.insert("inhale_voltage", QVariant(0));
  _ivt.insert("exhale_voltage", QVariant(0));
  _ivt.insert("purge_voltage" , QVariant(0));
  _ivt.insert("air_in_voltage", QVariant(0));
  _ivt.insert("o2_in_voltage" , QVariant(0));
  _ivt.insert("inhale_i2caddr", QVariant(0));
  _ivt.insert("exhale_i2caddr", QVariant(0));
  _ivt.insert("purge_i2caddr" , QVariant(0));
  _ivt.insert("air_in_i2caddr", QVariant(0));
  _ivt.insert("o2_in_i2caddr" , QVariant(0));
  _ivt.insert("system_temp"   , QVariant(0));
}

void DataSource::setupTargets()
{
  _targets.insert("UNKNOWN"   , new QQmlPropertyMap());
  _targets.insert("PC_AC"     , new QQmlPropertyMap());
  _targets.insert("PC_AC_PRVC", new QQmlPropertyMap());
  _targets.insert("PC_PSV"    , new QQmlPropertyMap());
  _targets.insert("CPAP"      , new QQmlPropertyMap());
  _targets.insert("TEST"      , new QQmlPropertyMap());
  _targets.insert("PURGE"     , new QQmlPropertyMap());
  _targets.insert("FLUSH"     , new QQmlPropertyMap());
  _targets.insert("CURRENT"   , new QQmlPropertyMap());
  setupTarget(*_targets["UNKNOWN"   ]);
  setupTarget(*_targets["PC_AC"     ]);
  setupTarget(*_targets["PC_AC_PRVC"]);
  setupTarget(*_targets["PC_PSV"    ]);
  setupTarget(*_targets["CPAP"      ]);
  setupTarget(*_targets["TEST"      ]);
  setupTarget(*_targets["PURGE"     ]);
  setupTarget(*_targets["FLUSH"     ]);
  setupTarget(*_targets["CURRENT"   ]);
}

void DataSource::setupTarget(QQmlPropertyMap &target)
{
  setupProperty(target);

  target.insert("mode"                    , QVariant(0));
  target.insert("inspiratory_pressure"    , QVariant(0));
  target.insert("ie_ratio"                , QVariant(0));
  target.insert("volume"                  , QVariant(0));
  target.insert("respiratory_rate"        , QVariant(0));
  target.insert("peep"                    , QVariant(0));
  target.insert("fiO2_percent"            , QVariant(0));
  target.insert("inhale_time"             , QVariant(0));
  target.insert("buffer_upper_pressure"   , QVariant(0));
  target.insert("buffer_lower_pressure"   , QVariant(0));
  target.insert("inhale_trigger_enable"   , QVariant(0));
  target.insert("exhale_trigger_enable"   , QVariant(0));
  target.insert("volume_trigger_enable"   , QVariant(0));
  target.insert("inhale_trigger_threshold", QVariant(0));
  target.insert("exhale_trigger_threshold", QVariant(0));
  //target.insert("pid_gain"                , QVariant(0));
}

void DataSource::setupBattery()
{
  setupProperty(_battery);

  _battery.insert("bat"         , QVariant(0));
  _battery.insert("ok"          , QVariant(0));
  _battery.insert("alarm"       , QVariant(0));
  _battery.insert("rdy2buf"     , QVariant(0));
  _battery.insert("bat85"       , QVariant(0));
  _battery.insert("prob_elec"   , QVariant(0));
  _battery.insert("dummy"       , QVariant(0));
}

void DataSource::setupPersonal()
{
  setupProperty(_personal);

  _personal.insert("name"  , QVariant("Person Person"));
  _personal.insert("patient_id"  , QVariant("4 8 15 16 23 42"));
  _personal.insert("age"   , QVariant(30));
  _personal.insert("sex"   , QVariant("o"));
  _personal.insert("height", QVariant(175));
  _personal.insert("weight", QVariant(80));
}

void DataSource::setupCommandReadback()
{
  QStringList cmdTypes = {"GET_THRESHOLD_MIN", "GET_THRESHOLD_MAX"};
  for (auto type: cmdTypes) {
    QVariantMap map;
    map.insert("UNKNOWN"                       , QVariant(0));
    map.insert("APNEA"                         , QVariant(0));
    map.insert("CHECK_VALVE_EXHALE"            , QVariant(0));
    map.insert("CHECK_P_PATIENT"               , QVariant(0));
    map.insert("EXPIRATION_SENSE_FAULT_OR_LEAK", QVariant(0));
    map.insert("EXPIRATION_VALVE_LEAK"         , QVariant(0));
    map.insert("HIGH_FIO2"                     , QVariant(0));
    map.insert("HIGH_PRESSURE"                 , QVariant(0));
    map.insert("HIGH_RR"                       , QVariant(0));
    map.insert("HIGH_VTE"                      , QVariant(0));
    map.insert("LOW_VTE"                       , QVariant(0));
    map.insert("HIGH_VTI"                      , QVariant(0));
    map.insert("LOW_VTI"                       , QVariant(0));
    map.insert("INTENTIONAL_STOP"              , QVariant(0));
    map.insert("LOW_BATTERY"                   , QVariant(0));
    map.insert("LOW_FIO2"                      , QVariant(0));
    map.insert("OCCLUSION"                     , QVariant(0));
    map.insert("HIGH_PEEP"                     , QVariant(0));
    map.insert("LOW_PEEP"                      , QVariant(0));
    map.insert("AC_POWER_DISCONNECTION"        , QVariant(0));
    map.insert("BATTERY_FAULT_SRVC"            , QVariant(0));
    map.insert("BATTERY_CHARGE"                , QVariant(0));
    map.insert("AIR_FAIL"                      , QVariant(0));
    map.insert("O2_FAIL"                       , QVariant(0));
    map.insert("PRESSURE_SENSOR_FAULT"         , QVariant(0));
    map.insert("ARDUINO_FAIL"                  , QVariant(0));
    _cmdReadback.insert(type, map);
  }
}

void DataSource::reset()
{
  _sets.clear();
}

void DataSource::import(QFile &file)
{
  QTextStream txt(&file);
  DataSet &dataSetPressure = _sets["pressure_inhale"];
  DataSet &dataSetFlow = _sets["flow"];
  DataSet &dataSetVolume = _sets["volume"];
  DataAxis &yAxisPressure = _axes[dataSetPressure.axisName];
  DataAxis &yAxisFlow = _axes[dataSetFlow.axisName];
  DataAxis &yAxisVolume = _axes[dataSetVolume.axisName];

  float timePrev = -1;
  while (!txt.atEnd()) {
    QString line = txt.readLine();
    QRegularExpression re_csv(
     QLatin1String("([-0-9.]+),([-0-9.]+),([-0-9.]+),([-0-9.]+)"));
    QRegularExpressionMatch match;
    if (!line.contains(re_csv, &match)) {
      continue;
    }
    float time = match.captured(1).toFloat();
    float pressure = match.captured(2).toFloat();
    float flow = match.captured(3).toFloat();
    float volume = match.captured(4).toFloat();
    //qDebug() << time
    //         << pressure
    //         << flow
    //         << volume;
    if (timePrev < 0) timePrev = time;
    int ms = ceil((time - timePrev) * 1000.0);

    addSample(dataSetPressure, yAxisPressure, pressure, ms);
    addSample(dataSetFlow, yAxisFlow, flow, ms);
    addSample(dataSetVolume, yAxisVolume, volume, ms);

    timePrev = time;
  }
}

void DataSource::pushBuffer(QByteArray b)
{
  _buffersMutex.lock();
  _buffers.append(b);
  _buffersNotEmpty.wakeAll();
  _buffersMutex.unlock();
}

QByteArray DataSource::popBuffer()
{
  // Wait for a message to be recieved
  _buffersMutex.lock();
  auto index = _buffers.indexOf('\0');
  if (index < 0) {
    _buffersNotEmpty.wait(&_buffersMutex);
  }
  // If there is a backlog of messages, skip to the last one
  const int messageCount = _buffers.count('\0');
  if (messageCount > 50) {
    qDebug() << "WARNING: Message backlog of" << messageCount << "messages, skipping forwards";
    // Ignore the last byte as valid messages end with a null byte
    _buffers = _buffers.mid(_buffers.lastIndexOf('\0', -2) + 1);
  }
  // Find the message and return it
  QByteArray data;
  index = _buffers.indexOf('\0');
  if (index < 0 ) {
    data = nullptr;
  } else {
    data = _buffers.left(index);
    _buffers = _buffers.mid(index+1);
  }
  _buffersMutex.unlock();
  return data;
}

void DataSource::broadcastConnect()
{
  _broadcastReceiver.connectToServer();
}

void DataSource::broadcastConnected()
{
  qDebug() << "Connected to" << _host << ":" << _port;
  setConnected(true);
}

void DataSource::broadcastDisconnect()
{
  _broadcastReceiver.disconnectFromServer();
}

void DataSource::broadcastDisconnected()
{
  qDebug() << "Disconnected";

  setConnected(false);
  _reconnectTimer.start(1000);
}

void DataSource::broadcastError(QAbstractSocket::SocketError error)
{
  qDebug() << error;
  emit notification(tr("Communication error"));
  _reconnectTimer.start(1000);
}

#define UPDATE_CONCURRENT

void DataSource::update()
{
  auto start = high_resolution_clock::now();
  auto it = _commands.begin();
  while (it != _commands.end()) {
    if ((*it)->state() == QAbstractSocket::UnconnectedState) {
      delete *it;
      it = _commands.erase(it);
    } else {
      ++it;
    }
  }
#ifdef UPDATE_CONCURRENT
  auto future = QtConcurrent::map(_sets, [this](DataSet &set) {
#else
  for (auto &set : _sets) {
#endif
    if (set.mutex->tryLock()) {
      if (!set.series) {
        set.mutex->unlock();
#ifdef UPDATE_CONCURRENT
        return;
#else
        continue;
#endif
      }
      set.visible = set.series->isVisible();
      if (!set.dirty) {
        set.mutex->unlock();
#ifdef UPDATE_CONCURRENT
        return;
#else
        continue;
#endif
      }
      set.dirty = false;
      QXYSeries *xySeries = static_cast<QXYSeries *>(set.series);
      xySeries->replace(set.points);
      if (set.mainSeries) {
        QXYSeries *mainSeries = static_cast<QXYSeries *>(set.mainSeries);
        mainSeries->replace(set.points);
      }
      set.mutex->unlock();
    }
    auto &axis = _axes[set.axisName];
    if (axis.mutex->tryLock()) {
      if (axis.dirty) {
        axis.dirty = false;
        auto plotAxes = set.series->attachedAxes();
        for (auto plotAxis : plotAxes) {
          if (!plotAxis->objectName().length()) {
            continue;
          }
          if(set.autoscale) {
            plotAxis->setRange(axis.min, axis.max);
          }
          break; //stop at the first named axis
        }
      }
      axis.mutex->unlock();
    }
#ifdef UPDATE_CONCURRENT
  });
  future.waitForFinished();
#else
  }
#endif
  //return _scrollTimer.restart();
  auto stop = high_resolution_clock::now();
  auto duration = duration_cast<microseconds>(stop - start);
  if (duration.count() > 1000.0/TARGET_FPS * 1000) {
    qDebug() << "WARNING: Drawing took longer than budgeted" << duration.count() << "us";
  }
}

void DataSource::raiseAlarm(QString message, QString priority)
{
  QDateTime since = QDateTime::currentDateTime();

  int existIdx = -1;
  for (int alarmIdx = 0; alarmIdx < _alarms.size(); alarmIdx++) {
    AlarmObject *alarm = qobject_cast<AlarmObject*>(_alarms.at(alarmIdx));
    if (alarm->message() == message && alarm->priority() == priority && !alarm->acked()) {
      existIdx = alarmIdx;
      break;
    }
  }

  if (existIdx != -1) {
    AlarmObject *alarm = qobject_cast<AlarmObject*>(_alarms.at(existIdx));
    alarm->setUntil(since);
  } else {
    _alarms.prepend(new AlarmObject(message, priority, since));
    emit alarm(message, priority);
    emit alarmsChanged();
  }
}

void DataSource::statusAlarm(QString message, QString priority)
{
  int existIdx = -1;
  for (int alarmIdx = 0; alarmIdx < _alarms.size(); alarmIdx++) {
    AlarmObject *alarm = qobject_cast<AlarmObject*>(_alarms.at(alarmIdx));
    if (message == "") {
      alarm->setAcked(true);
    } else if (alarm->message() == message && alarm->priority() == priority && !alarm->acked()) {
      existIdx = alarmIdx;
      break;
    }
  }

  if (existIdx != -1) {
    AlarmObject *alarm = qobject_cast<AlarmObject*>(_alarms.at(existIdx));
    alarm->setAcked(false);
  } else if (message != "") {
    QDateTime since = QDateTime::currentDateTime();
    _alarms.prepend(new AlarmObject(message, priority, since));
    emit alarm(message, priority);
  }
  emit alarmsChanged();
}

void DataSource::ackAlarms()
{
  for (auto &alarm : _alarms) {
    AlarmObject *alarm_object = qobject_cast<AlarmObject*>(alarm);
    if (!alarm_object->acked()) {
      sendAlarmAck(alarm_object->priority(), alarm_object->message());
    }
  }
}

void DataSource::sendMode(QString descr, QString mode)
{
  QJsonDocument json;
  QJsonObject cmd;
  cmd["type"] = "CMD";
  cmd["cmdtype"] = "SET_MODE";
  cmd["cmd"] = mode;
  cmd["param"]; // null
  json.setObject(cmd);

  sendCommand(descr, json);
}

void DataSource::sendStart()
{
  QJsonDocument json;
  QJsonObject cmd;
  cmd["type"] = "CMD";
  cmd["cmdtype"] = "GENERAL";
  cmd["cmd"] = "START";
  cmd["param"]; // null
  json.setObject(cmd);

  sendCommand("Start", json);
}

void DataSource::sendStandby()
{
  QJsonDocument json;
  QJsonObject cmd;
  cmd["type"] = "CMD";
  cmd["cmdtype"] = "GENERAL";
  cmd["cmd"] = "STANDBY";
  cmd["param"]; // null
  json.setObject(cmd);

  sendCommand("Standby", json);
}

void DataSource::sendStop()
{
  QJsonDocument json;
  QJsonObject cmd;
  cmd["type"] = "CMD";
  cmd["cmdtype"] = "GENERAL";
  cmd["cmd"] = "STOP";
  cmd["param"]; // null
  json.setObject(cmd);

  sendCommand("Stop", json);
}

void DataSource::sendAlarmAck(QString alarm_type, QString alarm_code)
{
  QJsonDocument json;
  QJsonObject cmd;
  cmd["type"] = "ALARM";
  cmd["alarm_type"] = alarm_type;
  cmd["alarm_code"] = alarm_code;
  cmd["param"] = 0;
  json.setObject(cmd);

  sendCommand(alarm_code + " alarm ack", json);
}

void DataSource::sendPersonal(QString name, QString patient_id, int age, QString sex, qreal height, qreal weight)
{
  QJsonDocument json;
  QJsonObject cmd;
  cmd["type"]         = "PERSONAL";
  cmd["name"]         = name;
  cmd["patient_id"]   = patient_id;
  cmd["sex"]          = sex;
  cmd["age"]          = age;
  cmd["height"]       = height;
  cmd["weight"]       = weight;
  json.setObject(cmd);
  qDebug() << json;
  sendCommand("SET_PERSONAL", json);
}

void DataSource::sendCommand(QString type, QString code, qreal param)
{
    QJsonDocument json;
    QJsonObject cmd;
    cmd["type"]    = "CMD";
    cmd["cmdtype"] = type;
    cmd["cmd"]     = code;
    cmd["param"]   = param;
    json.setObject(cmd);

    sendCommand(type + "." + code, json);
}

void DataSource::sendCommand(QString name, QJsonDocument json)
{
  CommandObject *co = new CommandObject(name, _host, _port - 1, json, this);
  emit commandCreated(name);
  connect(co, &CommandObject::sent, this, &DataSource::commandSent);
  connect(co, &CommandObject::acked, this, &DataSource::commandAcked);
  connect(co, &CommandObject::failed, this, &DataSource::commandFailed);
  _commands.append(co);
}

void DataSource::setupChart(QObject *object, QString objectName)
{
  QObject *chartObject = object->findChild<QObject *>(objectName);
  if (chartObject) {
    //chartObject is DeclarativeChart *, an internal type that can't be accessed directly
    int count = chartObject->property("count").toInt();
    for (int i = 0; i < count; ++i) {
      QAbstractSeries *series;
      QMetaObject::invokeMethod(
       chartObject, "series", Qt::AutoConnection, Q_RETURN_ARG(QAbstractSeries *, series), Q_ARG(int, i));
      QString objName = series->objectName();
      if (!objName.length()) {
        qDebug() << "Series '" << series->name() << "does not have an objectName";
        continue;
      }
      auto plotAxes = series->attachedAxes();
      for (auto plotAxis : plotAxes) {
        if (!plotAxis->objectName().length()) {
          continue;
        }
        auto valueAxis = static_cast<QValueAxis *>(plotAxis);
        auto &axis = _axes[plotAxis->objectName()];
        axis.minOrig = valueAxis->min();
        axis.min = axis.minOrig;
        axis.maxOrig = valueAxis->max();
        axis.max = axis.maxOrig;
        axis.dirty = false;
        _sets[objName].axisName = plotAxis->objectName();
        _sets[objName].points.reserve(MAX_SECONDS * 1000);
        break; //stop at the first named axis
      }
      QXYSeries *xySeries = static_cast<QXYSeries *>(series);
      QPen pen = xySeries->pen();
      pen.setWidth(3);
      xySeries->setPen(pen);

      _sets[objName].series = series;
      _sets[objName].points.clear();
      _sets[objName].dirty = false;
      _sets[objName].visible = series->isVisible();
    }
  } else {
    qDebug() << "ChartView '" << objectName << "' not found";
  }
}
