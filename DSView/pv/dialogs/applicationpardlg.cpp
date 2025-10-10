/*
 * This file is part of the DSView project.
 * DSView is based on PulseView.
 * 
 * Copyright (C) 2021 DreamSourceLab <support@dreamsourcelab.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
 */

#include "applicationpardlg.h"
#include "dsdialog.h"
#include <QCheckBox>
#include <QComboBox>
#include <QFontDatabase>
#include <QFormLayout>
#include <QGridLayout>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QObject>
#include <QScrollArea>
#include <QScrollBar>
#include <QSizePolicy>
#include <QString>
#include <QVBoxLayout>
#include <QWidget>
#include <vector>

#include "../config/appconfig.h"
#include "../ui/langresource.h"
#include "../appcontrol.h"
#include "../sigsession.h"
#include "../ui/dscombobox.h"
#include "../log.h"

namespace pv
{
namespace dialogs
{

ApplicationParamDlg::ApplicationParamDlg()
{
   
}

ApplicationParamDlg::~ApplicationParamDlg()
{
}

void ApplicationParamDlg::bind_font_name_list(QComboBox *box, QString v)
{   
    int selDex = -1;

    QString defName(L_S(STR_PAGE_DLG, S_ID(IDS_DLG_DEFAULT_FONT), "Default"));
    box->addItem(defName);

    if (_font_name_list.size() == 0)
    {
        QFontDatabase fDataBase;
        _font_name_list = fDataBase.families();
    }
   
    for (QString family : _font_name_list) {
        if (family.indexOf("[") == -1)
        {
            box->addItem(family);

            if (selDex == -1 && family == v){
                selDex = box->count() - 1;
            }
        }
    }

    if (selDex == -1)
        selDex = 0;

    box->setCurrentIndex(selDex);
}

void ApplicationParamDlg::bind_font_size_list(QComboBox *box, float size)
{   
    int selDex = -1;

    float minSize = 0;
    float maxSize = 0;

    AppConfig::GetFontSizeRange(&minSize, &maxSize);

    for(int i=minSize; i<=maxSize; i++)
    {
        box->addItem(QString::number(i));
        if (i == size){
            selDex = box->count() - 1;
        }
    }
    if (selDex == -1)
        selDex = 2;
    box->setCurrentIndex(selDex);
}

bool ApplicationParamDlg::ShowDlg(QWidget *parent)
{
    DSDialog dlg(parent, true, true);
    dlg.setTitle(L_S(STR_PAGE_DLG, S_ID(IDS_DLG_DISPLAY_OPTIONS), "Display options"));
    AppConfig &app = AppConfig::Instance();

    QVBoxLayout *lay = new QVBoxLayout();

    const float baseFontSize = 9.0f;
    const int baseSpacing = 10;
    float fSize = app.appOptions.fontSize;
    int dynamicSpacing = static_cast<int>(baseSpacing * (fSize / baseFontSize));
    lay->setContentsMargins(10, 10, 10, 10);
    lay->setSpacing(dynamicSpacing);

    QCheckBox *ck_quickScroll = new QCheckBox();
    ck_quickScroll->setChecked(app.appOptions.quickScroll);

    QCheckBox *ck_trigInMid = new QCheckBox();
    ck_trigInMid->setChecked(app.appOptions.trigPosDisplayInMid);

    QCheckBox *ck_profileBar = new QCheckBox();
    ck_profileBar->setChecked(app.appOptions.displayProfileInBar);

    QCheckBox *ck_abortData = new QCheckBox();
    ck_abortData->setChecked(app.appOptions.swapBackBufferAlways);

    QCheckBox *ck_autoScrollLatestData = new QCheckBox();
    ck_autoScrollLatestData->setChecked(app.appOptions.autoScrollLatestData);

    QComboBox *ftCbSize = new DsComboBox();
    bind_font_size_list(ftCbSize, app.appOptions.fontSize);

    QComboBox *tooltipFtCbSize = new DsComboBox();
    bind_font_size_list(tooltipFtCbSize, app.appOptions.tooltipFontSize);
   
    // Logic group
    QLabel *logicLabel = new QLabel(L_S(STR_PAGE_DLG, S_ID(IDS_DLG_GROUP_LOGIC), "Logic"));
    logicLabel->setStyleSheet(QString("font-weight: bold; font-size: %1pt; margin-bottom: -%2px;").arg(fSize).arg(static_cast<int>(fSize / 1.5)));
    QGroupBox *logicGroup = new QGroupBox();
    QGridLayout *logicLay = new QGridLayout();
    logicLay->setContentsMargins(10,15,15,10);
    logicGroup->setLayout(logicLay);
    logicLay->addWidget(new QLabel(L_S(STR_PAGE_DLG, S_ID(IDS_DLG_QUICK_SCROLL), "Quick scroll")), 0, 0, Qt::AlignLeft | Qt::AlignVCenter);
    logicLay->addWidget(ck_quickScroll, 0, 1, Qt::AlignRight | Qt::AlignVCenter);
    logicLay->addWidget(new QLabel(L_S(STR_PAGE_DLG, S_ID(IDS_DLG_USE_ABORT_DATA_REPEAT), "Used abort data")), 1, 0, Qt::AlignLeft | Qt::AlignVCenter);
    logicLay->addWidget(ck_abortData, 1, 1, Qt::AlignRight | Qt::AlignVCenter);
    logicLay->addWidget(new QLabel(L_S(STR_PAGE_DLG, S_ID(IDS_DLG_AUTO_SCROLL_LATEAST_DATA), "Auto scoll latest")), 2, 0, Qt::AlignLeft | Qt::AlignVCenter);
    logicLay->addWidget(ck_autoScrollLatestData, 2, 1, Qt::AlignRight | Qt::AlignVCenter);
    
    QVBoxLayout *logicContainer = new QVBoxLayout();
    logicContainer->setSpacing(0);
    logicContainer->addWidget(logicLabel, 0, Qt::AlignHCenter);
    logicContainer->addWidget(logicGroup);
    lay->addLayout(logicContainer);

    //Scope group
    QLabel *dsoLabel = new QLabel(L_S(STR_PAGE_DLG, S_ID(IDS_DLG_GROUP_DSO), "Scope"));
    dsoLabel->setStyleSheet(QString("font-weight: bold; font-size: %1pt; margin-bottom: -%2px;").arg(fSize).arg(static_cast<int>(fSize / 1.5)));
    QGroupBox *dsoGroup = new QGroupBox();
    QGridLayout *dsoLay = new QGridLayout();
    dsoLay->setContentsMargins(10,15,15,10);
    dsoGroup->setLayout(dsoLay);
    dsoLay->addWidget(new QLabel(L_S(STR_PAGE_DLG, S_ID(IDS_DLG_TRIG_DISPLAY_MIDDLE), "Tig pos in middle")), 0, 0, Qt::AlignLeft | Qt::AlignVCenter);
    dsoLay->addWidget(ck_trigInMid, 0, 1, Qt::AlignRight | Qt::AlignVCenter);

    QVBoxLayout *dsoContainer = new QVBoxLayout();
    dsoContainer->setSpacing(0);
    dsoContainer->addWidget(dsoLabel, 0, Qt::AlignHCenter);
    dsoContainer->addWidget(dsoGroup);
    lay->addLayout(dsoContainer);

    //UI
    QLabel *uiLabel = new QLabel(L_S(STR_PAGE_DLG, S_ID(IDS_DLG_GROUP_UI), "UI"));
    uiLabel->setStyleSheet(QString("font-weight: bold; font-size: %1pt; margin-bottom: -%2px;").arg(fSize).arg(static_cast<int>(fSize / 1.5)));
    QGroupBox *uiGroup = new QGroupBox();
    QGridLayout *uiLay = new QGridLayout();
    uiLay->setContentsMargins(10,15,15,10);
    uiGroup->setLayout(uiLay);
    uiLay->addWidget(new QLabel(L_S(STR_PAGE_DLG, S_ID(IDS_DLG_DISPLAY_PROFILE_IN_BAR), "Profile in bar")), 0, 0, Qt::AlignLeft | Qt::AlignVCenter);
    uiLay->addWidget(ck_profileBar, 0, 1, Qt::AlignRight | Qt::AlignVCenter);
    uiLay->addWidget(new QLabel(L_S(STR_PAGE_DLG, S_ID(IDS_DLG_FONT_SIZE), "Font size")), 1, 0, Qt::AlignLeft | Qt::AlignVCenter);
    uiLay->addWidget(ftCbSize, 1, 1, Qt::AlignRight | Qt::AlignVCenter);
    uiLay->addWidget(new QLabel(L_S(STR_PAGE_DLG, S_ID(IDS_DLG_TOOLTIP_FONT_SIZE), "Tooltip font size")), 2, 0, Qt::AlignLeft | Qt::AlignVCenter);
    uiLay->addWidget(tooltipFtCbSize, 2, 1, Qt::AlignRight | Qt::AlignVCenter);

    QVBoxLayout *uiContainer = new QVBoxLayout();
    uiContainer->setSpacing(0);
    uiContainer->addWidget(uiLabel, 0, Qt::AlignHCenter);
    uiContainer->addWidget(uiGroup);
    lay->addLayout(uiContainer);

    dlg.layout()->addLayout(lay);
    dlg.adjustSize();
    dlg.exec();
    bool ret = dlg.IsClickYes();

    //save config
    if (ret){

        bool bAppChanged = false;
        bool bFontChanged = false;
        float fSize = ftCbSize->currentText().toFloat();
        float tooltipFSize = tooltipFtCbSize->currentText().toFloat();

        if (app.appOptions.quickScroll != ck_quickScroll->isChecked()){
            app.appOptions.quickScroll = ck_quickScroll->isChecked();
            bAppChanged = true;
        }       
        if (app.appOptions.trigPosDisplayInMid != ck_trigInMid->isChecked()){
            app.appOptions.trigPosDisplayInMid = ck_trigInMid->isChecked();
            bAppChanged = true;
        }
        if (app.appOptions.displayProfileInBar != ck_profileBar->isChecked()){
            app.appOptions.displayProfileInBar = ck_profileBar->isChecked();
            bAppChanged = true;
        }
        if (app.appOptions.swapBackBufferAlways != ck_abortData->isChecked()){
            app.appOptions.swapBackBufferAlways = ck_abortData->isChecked();
            bAppChanged = true;
        }        
        if (app.appOptions.fontSize != fSize){
            app.appOptions.fontSize = fSize;
            bFontChanged = true;
        }
        if (app.appOptions.tooltipFontSize != tooltipFSize){
            app.appOptions.tooltipFontSize = tooltipFSize;
            bFontChanged = true;
        }
        if (app.appOptions.autoScrollLatestData != ck_autoScrollLatestData->isChecked()){
            app.appOptions.autoScrollLatestData = ck_autoScrollLatestData->isChecked();
            bAppChanged = true;
        }
 
        if (bAppChanged){
            app.SaveApp();
            AppControl::Instance()->GetSession()->broadcast_msg(DSV_MSG_APP_OPTIONS_CHANGED);
        }
        
        if (bFontChanged){
            if (!bAppChanged){
                app.SaveApp();
            }
            AppControl::Instance()->GetSession()->broadcast_msg(DSV_MSG_FONT_OPTIONS_CHANGED);
        }
    }
   
   return ret;
}
 

} //
}//
