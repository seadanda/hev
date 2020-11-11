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


#include <QApplication>
#include <QtCore/QCommandLineParser>
#include <QtCore/QLoggingCategory>
#include <QtCore/QRegularExpression>
//#include <QtQuickControls2/QQuickStyle>
#include <QtQml/QQmlApplicationEngine>
#include <QtQml/QQmlContext>
#include <QtGui/QIcon>
#include <QTranslator>
#include "datasource.h"
#include "localization.h"

#ifndef VERSION
# define VERSION "WIP"
#endif

int main(int argc, char *argv[])
{
  QString host = "localhost";
  quint16 port = 54322;

  qputenv("QT_IM_MODULE", QByteArray("qtvirtualkeyboard"));
  QApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
  //QGuiApplication app(argc, argv);
  // Qt Charts uses Qt Graphics View Framework for drawing, therefore QApplication must be used.
  QApplication app(argc, argv);
  app.setWindowIcon(QIcon(":/svg/icon.png"));

  QCommandLineParser cli;
  QCommandLineOption cli_server(QStringList() << "server",
   QApplication::translate("server", "Server address"),
   QApplication::translate("server", "[<host>]:<port>"));
  cli.addOption(cli_server);
  QCommandLineOption cli_size(QStringList() << "size",
   QApplication::translate("size", "Override minimum window size"),
   QApplication::translate("size", "<width>x<height>"));
  cli.addOption(cli_size);
  QCommandLineOption cli_import(QStringList() << "import",
   QApplication::translate("import", "Import data from CSV"),
   QApplication::translate("csv", "<path>.csv"));
  cli.addOption(cli_import);
  QCommandLineOption cli_opengl(QStringList() << "opengl",
   QApplication::translate("opengl", "Enable OpenGL acceleration"));
  cli.addOption(cli_opengl);
  cli.process(app);

  QString cli_server_str = cli.value(cli_server);
  if (cli_server_str.length()) {
    QRegularExpression re_server(
     QLatin1String("([a-z0-9-.]+)?:(\\d+)"), QRegularExpression::CaseInsensitiveOption);
    QRegularExpressionMatch match;
    if (cli_server_str.contains(re_server, &match)) {
      host = match.captured(1);
      if (!host.length()) { host = "localhost"; }
      port = match.captured(2).toUShort();
      qDebug() << "Server: " << host << ":" << port;
    } else {
      qDebug() << "Invalid server '" << cli_server_str << "'";
    }
  }

  //QQuickStyle::setStyle("Fusion");

  QQmlApplicationEngine engine;
  QQmlContext *rootContext = engine.rootContext();
  DataSource dataSource(host, port, nullptr);
  Localization localization(&engine);
  rootContext->setContextProperty("version", QString(VERSION));
  rootContext->setContextProperty("dataSource", &dataSource);
  rootContext->setContextProperty("readback", dataSource.readback());
  rootContext->setContextProperty("cycle"   , dataSource.cycle   ());
  rootContext->setContextProperty("fastdata", dataSource.data    ());
  rootContext->setContextProperty("ivt"     , dataSource.ivt     ());
  rootContext->setContextProperty("battery" , dataSource.battery ());
  rootContext->setContextProperty("personal", dataSource.personal());
  rootContext->setContextProperty("target_CURRENT"      , dataSource.target  ("CURRENT"   ));
  rootContext->setContextProperty("target_PC_AC"        , dataSource.target  ("PC_AC"     ));
  rootContext->setContextProperty("target_PC_AC_PRVC"   , dataSource.target  ("PC_AC_PRVC"));
  rootContext->setContextProperty("target_PC_PSV"       , dataSource.target  ("PC_PSV"    ));
  rootContext->setContextProperty("target_PC_PSV"       , dataSource.target  ("PC_PSV"    ));
  rootContext->setContextProperty("target_CPAP"         , dataSource.target  ("CPAP"      ));
  rootContext->setContextProperty("target_TEST"         , dataSource.target  ("TEST"      ));
  rootContext->setContextProperty("target_PURGE"        , dataSource.target  ("PURGE"     ));
  rootContext->setContextProperty("target_FLUSH"        , dataSource.target  ("FLUSH"     ));

  rootContext->setContextProperty("localization", &localization);

  engine.load(QUrl("qrc:/main.qml"));
  QObject *rootObject = engine.rootObjects().first();
  dataSource.setup(rootObject);

  //QQmlContext *windowContext = engine.contextForObject(rootObject);

  QString cli_import_str = cli.value(cli_import);
  if (cli_import_str.length()) {
    QFile file(cli_import_str);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
      qDebug() << "Unable to open file '" << cli_import_str << "'";
    }
    dataSource.import(file);
  }

  if (cli.isSet(cli_opengl)) {
    rootObject->setProperty("openGL", true);
  }
  QString cli_size_str = cli.value(cli_size);
  if (cli_size_str.length()) {
    QRegularExpression re_size(QLatin1String("(\\d+)x(\\d+)"));
    QRegularExpressionMatch match;
    if (cli_size_str.contains(re_size, &match)) {
      rootObject->setProperty("width", match.captured(1).toInt());
      rootObject->setProperty("height", match.captured(2).toInt());
      qDebug() << "Root size: " << rootObject->property("width") << "x" << rootObject->property("height");
    } else {
      qDebug() << "Invalid size '" << cli_size_str << "'";
    }
  }
  return app.exec();
}
