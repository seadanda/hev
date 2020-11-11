TARGET = hev-display
INCLUDEPATH += sources

QT += quick quickcontrols2 svg charts network concurrent

SOURCES += sources/main.cpp \
    sources/datasource.cpp \
    sources/localization.cpp \

HEADERS += \
    sources/datasource.h \
    sources/localization.h \

OTHER_FILES += \
    assets/*.qml \
    assets/svg/*.svg

RESOURCES += \
    assets/resources.qrc

lupdate_only {
    SOURCES += assets/*.qml
}

ICON = assets/svg/icon.ico

TRANSLATIONS = languages/translation-qml_fr.ts \
               languages/translation-qml_en.ts \
               languages/translation-qml_de.ts \
               languages/translation-qml_it.ts \
               languages/translation-qml_sk.ts \
               languages/translation-qml_lv.ts \
               languages/translation-qml_es.ts

CONFIG += lrelease embed_translations
