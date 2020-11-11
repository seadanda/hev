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


#ifndef DATASOURCE_H
#define DATASOURCE_H

#include <QtCore/QElapsedTimer>
#include <QtCore/QFile>
#include <QtCore/QJsonDocument>
#include <QtCore/QObject>
#include <QtCore/QThread>
#include <QtCore/QTime>
#include <QtCore/QTimer>
#include <QtCore/QWaitCondition>
#include <QtCharts/QAbstractSeries>
#include <QMutex>
#include <QTcpSocket>
#include <QQmlPropertyMap>

QT_CHARTS_USE_NAMESPACE

struct DataSet
{
  QMutex *mutex = new QMutex(); //We never remove a dataset until termination
  QAbstractSeries *series = nullptr;
  QAbstractSeries *mainSeries = nullptr;
  QVector<QPointF> points;
  QString axisName;
  bool dirty = false;
  bool visible = true;
  bool autoscale = true;
};
typedef QMap<QString, DataSet> DataSets;

struct DataAxis
{
  QMutex *mutex = new QMutex(); //We never remove an axis until termination
  qreal minOrig;
  qreal maxOrig;
  qreal min;
  qreal max;
  bool dirty = false;
};
typedef QMap<QString, DataAxis> DataAxes;

class AlarmObject : public QObject
{
  Q_OBJECT

  Q_PROPERTY(bool acked READ acked WRITE setAcked NOTIFY ackedChanged)
  Q_PROPERTY(QString priority READ priority NOTIFY priorityChanged)
  Q_PROPERTY(QString message READ message NOTIFY messageChanged)
  Q_PROPERTY(QDateTime since READ since NOTIFY sinceChanged)
  Q_PROPERTY(QDateTime until READ until WRITE setUntil NOTIFY untilChanged)

signals:
  void ackedChanged();
  void priorityChanged();
  void messageChanged();
  void sinceChanged();
  void untilChanged();

public:
  AlarmObject(QString message, QString priority, QDateTime since = QDateTime::currentDateTime(), QObject *parent = nullptr);

  bool acked() const { return _acked; }
  void setAcked(bool acked) {
    if (acked != _acked) {
      _acked = acked;
      emit ackedChanged();
    }
  }

  QString priority() const { return _priority; }
  QString message()  const { return _message; }
  QDateTime since()  const { return _since; }

  QDateTime until() const { return _until; }
  void setUntil(QDateTime until) {
    if (until != _until) {
      _until = until;
      emit untilChanged();
    }
  }

private:
  bool _acked = false;
  const QString _priority;
  const QString _message;
  const QDateTime _since;
  QDateTime _until;
};
typedef QList<AlarmObject *> AlarmObjects;

class DataSource;
class BroadcastReceiver : public QObject
{
  Q_OBJECT

public:
  explicit BroadcastReceiver(QString host, quint16 port, DataSource &source, QObject *parent = nullptr);

  void connectToServer();
  void disconnectFromServer();

signals:
  void connected();
  void disconnected();
  void error(QAbstractSocket::SocketError error);

public slots:
  void receive();

private:
  const QString _host;
  const quint16 _port;
  QTcpSocket _sock;
  DataSource &_source;
};

class BroadcastParser : public QThread
{
  Q_OBJECT

public:
  explicit BroadcastParser(DataSets &sets, DataAxes &axes, DataSource &source, QObject *parent = nullptr);

  void finish() { _parsing = false; }

private:
  // Alternatively, this could be a slot triggered by the receiver (which actually appears to be a bit faster)
  void run() override;

  void parse(QJsonObject &items, QQmlPropertyMap *map);
  void parseData(QJsonObject &json);
  void parseAlarm(QJsonObject &json);

  void parseActiveAlarms(QJsonObject &json);

signals:
  void alarm(QString message, QString priority);
  void alarmActive(QString message, QString priority);

private:
  qint64 _timestampPrevious = std::numeric_limits<qint64>::min();
  bool _parsing = true;

  DataSource &_source;
  DataSets &_sets;
  QMutex _setsMutex;
  DataAxes &_axes;
  QElapsedTimer _timer;
};

class CommandObject : public QObject
{
  Q_OBJECT

public:
  CommandObject(QString name, QString host, quint16 port, QJsonDocument json, QObject *parent = nullptr);

  QAbstractSocket::SocketState state() const { return _sock.state(); }

signals:
  void sent(QString name);
  void acked(QString name);
  void failed(QString name);

private slots:
  void connected();
  void replied();
  void disconnected();

private:
  const QString _name;
  QTcpSocket _sock;
  const QJsonDocument _json;
  QByteArray _buffer;
  bool _acked;
};

class DataSource : public QObject
{
  Q_OBJECT

  // Properties received from the server are read-only, properties settable by an operator are read-write
  // (in alphabetical order)
  Q_PROPERTY(QList<QObject *> alarms READ alarms NOTIFY alarmsChanged)
  Q_PROPERTY(bool connected READ connected NOTIFY connectedChanged)
  Q_PROPERTY(bool exhaleTrigger READ exhaleTrigger NOTIFY exhaleTriggerChanged)
  Q_PROPERTY(bool inhaleTrigger READ inhaleTrigger WRITE setInhaleTrigger NOTIFY inhaleTriggerChanged)
  Q_PROPERTY(int patientAge READ patientAge WRITE setPatientAge NOTIFY patientAgeChanged)
  Q_PROPERTY(QString patientName READ patientName WRITE setPatientName NOTIFY patientNameChanged)
  Q_PROPERTY(QString patientSurname READ patientSurname WRITE setPatientSurname NOTIFY patientSurnameChanged)
  Q_PROPERTY(QString patientId READ patientId WRITE setPatientId NOTIFY patientIdChanged)
  Q_PROPERTY(qreal patientWeight READ patientWeight WRITE setPatientWeight NOTIFY patientWeightChanged)
  Q_PROPERTY(QVariantMap cmdReadback READ cmdReadback WRITE setCmdReadback NOTIFY cmdReadbackChanged)

public:
  explicit DataSource(QString host, quint16 port, QObject *parent = 0);
  virtual ~DataSource();

  QList<QObject *> alarms() const { return _alarms; }

  QQmlPropertyMap *cycle()    { return &_cycle   ; }
  QQmlPropertyMap *data()     { return &_data    ; }
  QQmlPropertyMap *ivt()      { return &_ivt     ; }
  QQmlPropertyMap *readback() { return &_readback; }
  QQmlPropertyMap *battery()  { return &_battery ; }
  QQmlPropertyMap *personal() { return &_personal; }
  QQmlPropertyMap *target(QString mode)     { return _targets[mode]  ; }

  // Append here signal getters/setters for every Q_PROPERTY that should be exposed to the UI
  // (in alphabetical order)
  const QVariantMap &cmdReadback() { return _cmdReadback; }
//  const QString cmd, const QString key, const QVariant value
  void setCmdReadback(QVariantMap map) {
    QString key = map.keys()[0];
    _cmdReadback[key] = map[key];
    emit cmdReadbackChanged();
  }

  bool connected() const { return _connected; }
  void setConnected(bool connected) {
    if (connected != _connected) {
      _connected = connected;
      emit connectedChanged();
    }
  }

  bool exhaleTrigger() const { return _exhaleTrigger; }
  void setExhaleTrigger(bool exhaleTrigger) {
    if (exhaleTrigger != _exhaleTrigger) {
      _exhaleTrigger = exhaleTrigger;
      emit exhaleTriggerChanged();
    }
  }

  bool inhaleTrigger() const { return _inhaleTrigger; }
  void setInhaleTrigger(bool inhaleTrigger) {
    if (inhaleTrigger != _inhaleTrigger) {
      _inhaleTrigger = inhaleTrigger;
      emit inhaleTriggerChanged();
    }
  }

  int patientAge() const { return _patientAge; }
  void setPatientAge(int patientAge) {
    if (patientAge != _patientAge) {
      _patientAge = patientAge;
      emit patientAgeChanged();
    }
  }

  const QString &patientName() const { return _patientName; }
  void setPatientName(QString patientName) {
    if (patientName != _patientName) {
      _patientName = patientName;
      emit patientNameChanged();
    }
  }

  const QString &patientSurname() const { return _patientSurname; }
  void setPatientSurname(QString patientSurname) {
    if (patientSurname != _patientSurname) {
      _patientSurname = patientSurname;
      emit patientSurnameChanged();
    }
  }

  const QString &patientId() const { return _patientId; }
  void setPatientId(QString patientId) {
    if (patientId != _patientId) {
      _patientId = patientId;
      emit patientIdChanged();
    }
  }

  int patientWeight() const { return _patientWeight; }
  void setPatientWeight(int patientWeight) {
    if (patientWeight != _patientWeight) {
      _patientWeight = patientWeight;
      emit patientWeightChanged();
    }
  }

  // End of Q_PROPERTY getters/setters

  void setup(QObject *mainWindow);
  void reset();

  void import(QFile &file);

  void pushBuffer(QByteArray b);
  QByteArray popBuffer();

signals:
  void alarm(const QString &message, const QString &priority);
  void commandCreated(const QString &name);
  void commandSent(const QString &name);
  void commandAcked(const QString &name);
  void commandFailed(const QString &name);
  void notification(const QString &message);

  void dataChanged(const QString &key, const QVariant &value);
  void readbackChanged(const QString &key, const QVariant &value);
  void cycleChanged(const QString &key, const QVariant &value);
  void ivtChanged(const QString &key, const QVariant &value);
  void targetChanged(const QString &mode, const QString &key, const QVariant &value);
  void batteryChanged(const QString &key, const QVariant &value);
  void personalChanged(const QString &key, const QVariant &value);

  // Append here signal emitters for every Q_PROPERTY that should be exposed to the UI
  // (in alphabetical order)
  void alarmsChanged();

  void cmdReadbackChanged();
  void connectedChanged();
  void exhaleTriggerChanged();
  void inhaleTriggerChanged();
  void patientAgeChanged();
  void patientNameChanged();
  void patientSurnameChanged();
  void patientIdChanged();
  void patientWeightChanged();

public slots:
  void broadcastConnect();
  void broadcastConnected();
  void broadcastDisconnect();
  void broadcastDisconnected();
  void broadcastError(QAbstractSocket::SocketError error);

  void update();

  void raiseAlarm(QString message, QString priority);
  void statusAlarm(QString message, QString priority);
  void ackAlarms();

  void sendMode(QString descr, QString mode);
  void sendStart();
  void sendStandby();
  void sendStop();
  void sendAlarmAck(QString alarm_type, QString alarm_code);

  void sendCommand(QString type, QString code, qreal param);
  void sendPersonal(QString name, QString patient_id, int age, QString sex, qreal height, qreal weight);

private:
  void setupChart(QObject *object, QString objectName);
  void setupProperty(QQmlPropertyMap &property);
  void setupReadback();
  void setupData();
  void setupCycle();
  void setupIvt();
  void setupTarget(QQmlPropertyMap &target);
  void setupTargets();
  void setupBattery();
  void setupPersonal();
  void setupCommandReadback();

  void sendCommand(QString name, QJsonDocument json);

  const QString _host;
  const quint16 _port;

  QTimer _reconnectTimer;
  QThread _broadcastReceiverThread;
  BroadcastReceiver _broadcastReceiver;
  QMutex _buffersMutex;
  QWaitCondition _buffersNotEmpty;
  QByteArray _buffers;
  BroadcastParser _broadcastParser;

  QMap<QString, DataSet> _sets;
  QMap<QString, DataAxis> _axes;
  QTimer _updateTimer;
  //QElapsedTimer _scrollTimer;
  QTime _lastTime;
  QList<QObject *> _alarms;
  QList<CommandObject *> _commands;

  // Append here every Q_PROPERTY that should be exposed to the UI
  // (in alphabetical order)
  QQmlPropertyMap _cycle;
  QQmlPropertyMap _data;
  QQmlPropertyMap _ivt;
  QQmlPropertyMap _readback;
  QQmlPropertyMap _battery;
  QQmlPropertyMap _personal;
  QMap<QString, QQmlPropertyMap*> _targets;

  QVariantMap _cmdReadback;
  bool _connected = false;
  bool _exhaleTrigger = false;
  bool _inhaleTrigger = false;
  int _patientAge = 58;
  QString _patientName = "John";
  QString _patientSurname = "Smith";
  QString _patientId = "abc1234";
  qreal _patientWeight = 89;
};

#endif // DATASOURCE_H
