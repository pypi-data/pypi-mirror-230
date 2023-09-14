import sys
import os
import traceback
import decimal
import datetime as dt
from datetime import datetime, timedelta
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtCore import *
import sip
import matplotlib.pyplot as plt
from cheltuieli import chelt_plan
from mysqlquerys import connect


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        path2src, pyFileName = os.path.split(__file__)
        uiFileName = 'chelt_plan.ui'
        path2GUI = os.path.join(path2src, 'GUI', uiFileName)
        Ui_MainWindow, QtBaseClass = uic.loadUiType(path2GUI)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ini_file = r"D:\Python\MySQL\config.ini"
        self.ui.GB_planned_expenses.setVisible(False)
        self.gb_available_databases = self.ui.GB_databases
        self.append_databases_to_box()

        self.ui.cbActiveConto.currentIndexChanged.connect(self.get_table_info)
        self.ui.CBMonths.currentIndexChanged.connect(self.populateDatesInterval)
        self.ui.DEFrom.dateTimeChanged.connect(self.get_table_info)
        self.ui.DEBis.dateTimeChanged.connect(self.get_table_info)
        self.ui.planTable.horizontalHeader().sectionClicked.connect(self.sortPlan)
        self.ui.PB_plotTablePie.clicked.connect(self.plotTablePie)
        self.ui.PB_plotNamePie.clicked.connect(self.plotNamePie)
        self.ui.PB_Plot.clicked.connect(self.plotGraf)
        # self.ui.PB_export.clicked.connect(self.export)


    @property
    def available_databases(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        con = connect.DbConnection(self.ini_file)
        available_databases = con.databases
        return available_databases

    def append_databases_to_box(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        if self.gb_available_databases.layout() is not None:
            self.delete_items_of_layout()
        vbox = QVBoxLayout()
        for i, db in enumerate(self.available_databases):
            rb = QRadioButton(db)
            rb.toggled.connect(self.connect_to_db)
            vbox.addWidget(rb)
        self.gb_available_databases.setLayout(vbox)

    def delete_items_of_layout(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        layout_grupa = self.gb_available_databases.layout()
        if layout_grupa is not None:
            while layout_grupa.count():
                item = layout_grupa.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    delete_items_of_layout(item.layout())
            sip.delete(layout_grupa)

    def connect_to_db(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        print('self.sender().objectName()', self.sender().text())
        self.ui.GB_planned_expenses.setVisible(True)
        self.populateCBMonths()
        self.populateDatesInterval()
        self.get_table_info(self.sender().text())
        # self.populateCBConto()

    def get_table_info(self, database_name):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        displayTableHead = ['table', 'name', 'value', 'myconto', 'payDay', 'freq']
        selectedStartDate = self.ui.DEFrom.date().toPyDate()
        selectedEndDate = self.ui.DEBis.date().toPyDate()
        self.app = chelt_plan.CheltuieliPlanificate(self.ini_file, database_name)
        tableHead, payments4Interval, income = self.app.prepareTablePlan(self.ui.cbActiveConto.currentText(), selectedStartDate, selectedEndDate)

        self.populateExpensesPlan(tableHead, payments4Interval, displayTableHead)
        self.populateTree(tableHead, payments4Interval)
        self.populateIncomePlan(tableHead, income, displayTableHead)
        self.totals()

    # def export(self):
    #     print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
    #     expName, _ = QFileDialog.getSaveFileName(self, "Save file", "", "Excel Files (*.xlsx)")
    #     worksheets = [('Complete', datetime(datetime.now().year, 1, 1),datetime(datetime.now().year, 12, 31))]
    #     for mnth in range(1, 13):
    #         firstDayOfMonth = datetime(datetime.now().year, mnth, 1)
    #         if mnth != 12:
    #             lastDayOfMonth = datetime(datetime.now().year, mnth+1, 1) - timedelta(days=1)
    #         else:
    #             lastDayOfMonth = datetime(datetime.now().year + 1, 1, 1) - timedelta(days=1)
    #
    #         tup = (firstDayOfMonth.strftime("%B"), firstDayOfMonth, lastDayOfMonth)
    #         worksheets.append(tup)
    #
    #     wb = Workbook()
    #     ws = wb.active
    #     for mnth, firstDayOfMonth, lastDayOfMonth in worksheets:
    #         # print(mnth, firstDayOfMonth, lastDayOfMonth)
    #         if mnth == 'Complete':
    #             ws.title = mnth
    #         else:
    #             wb.create_sheet(mnth)
    #         ws = wb[mnth]
    #         self.ui.DEFrom.setDate(QDate(firstDayOfMonth))
    #         self.ui.DEBis.setDate(QDate(lastDayOfMonth))
    #         self.prepareTablePlan()
    #
    #         planExpenseTable, planExpenseTableHead = self.readPlanExpenses()
    #         cheltData = np.insert(planExpenseTable, 0, planExpenseTableHead, 0)
    #
    #         for i, row in enumerate(cheltData):
    #             for j, col in enumerate(row):
    #                 ws.cell(row=i + 1, column=j + 1).value = cheltData[i][j]
    #
    #         firstRow = 1
    #         firstCol = get_column_letter(1)
    #         lastRow = len(cheltData)
    #         lastCol = get_column_letter(len(cheltData[0]))
    #
    #         table_title = '{}_{}'.format('chelt', mnth )
    #         new_text = ('{}{}:{}{}'.format(firstCol, firstRow, lastCol, lastRow))
    #         tab = Table(displayName=table_title, ref=new_text)
    #         # Add a default style with striped rows and banded columns
    #         style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
    #                                showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    #         tab.tableStyleInfo = style
    #         ws.add_table(tab)
    #         ws.cell(row=lastRow + 1, column=1).value = 'Total Number of Expenses'
    #         ws.cell(row=lastRow + 1, column=2).value = self.ui.LEtotalNoOfTransactions.text()
    #         ws.cell(row=lastRow + 2, column=1).value = 'Total Expenses'
    #         ws.cell(row=lastRow + 2, column=2).value = self.ui.LEtotalValue.text()
    #         #######income
    #
    #         planIncomeTable, planIncomeTableHead = self.readPlanIncome()
    #         incomeData = np.insert(planIncomeTable, 0, planIncomeTableHead, 0)
    #         firstRow = lastRow + 5
    #         firstCol = get_column_letter(1)
    #         lastRow = firstRow + len(incomeData)
    #         lastCol = get_column_letter(len(incomeData[0]))
    #
    #         for i, row in enumerate(incomeData):
    #             for j, col in enumerate(row):
    #                 ws.cell(row=i + firstRow, column=j + 1).value = incomeData[i][j]
    #
    #         table_title = '{}_{}'.format('income', mnth )
    #         new_text1 = ('{}{}:{}{}'.format(firstCol, firstRow, lastCol, lastRow))
    #         tab = Table(displayName=table_title, ref=new_text1)
    #         # Add a default style with striped rows and banded columns
    #         style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
    #                                showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    #         tab.tableStyleInfo = style
    #         ws.add_table(tab)
    #         ws.cell(row=lastRow + 1, column=1).value = 'Total Number of Incomes'
    #         ws.cell(row=lastRow + 1, column=2).value = self.ui.LEtotalNoOfIncome.text()
    #         ws.cell(row=lastRow + 2, column=1).value = 'Total Income'
    #         ws.cell(row=lastRow + 2, column=2).value = self.ui.LEtotalIncome.text()
    #
    #     wb.save(expName)

    def populateCBMonths(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        self.ui.CBMonths.addItem('interval')
        months = [dt.date(2000, m, 1).strftime('%B') for m in range(1, 13)]
        for month in months:
            self.ui.CBMonths.addItem(month)

    def populateCBConto(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        self.ui.cbActiveConto.addItem('all')
        self.ui.cbActiveConto.addItems(self.app.myContos)

    def populateDatesInterval(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        startDate = QDate(datetime.now().year, datetime.now().month, datetime.now().day)
        if datetime.now().month != 12:
            mnth = datetime.now().month + 1
            lastDayOfMonth = datetime(datetime.now().year, mnth, 1) - timedelta(days=1)
        else:
            lastDayOfMonth = datetime(datetime.now().year + 1, 1, 1) - timedelta(days=1)

        if self.ui.CBMonths.currentText() != 'interval':
            mnth = datetime.strptime(self.ui.CBMonths.currentText(), "%B").month
            # print('****', mnth)
            # if mnth == 1:
            #     startDate = datetime(datetime.now().year - 1, 12, 30)
            # elif mnth == 2:
            #     startDate = datetime(datetime.now().year, mnth-1, 28)
            # else:
            #     startDate = datetime(datetime.now().year, mnth-1, 30)
            #
            # lastDayOfMonth = datetime(datetime.now().year, mnth, 29)

            startDate = datetime(datetime.now().year, mnth, 1)
            if mnth != 12:
                lastDayOfMonth = datetime(datetime.now().year, mnth+1, 1) - timedelta(days=1)
            else:
                lastDayOfMonth = datetime(datetime.now().year + 1, 1, 1) - timedelta(days=1)

            startDate = startDate - timedelta(days=2)
            lastDayOfMonth = lastDayOfMonth - timedelta(days=2)

            startDate = QDate(startDate)
            lastDayOfMonth = QDate(lastDayOfMonth)

        self.ui.DEFrom.setDate(startDate)
        self.ui.DEBis.setDate(lastDayOfMonth)

        self.ui.DEFrom.setCalendarPopup(True)
        self.ui.DEBis.setCalendarPopup(True)

    def populateTree(self, tableHead, table):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        self.ui.TWmnthVSIrreg.clear()
        self.ui.TWmnthVSIrreg.setHeaderLabels(['freq', 'name', 'value'])
        monthly_level = QTreeWidgetItem(self.ui.TWmnthVSIrreg)
        monthly_level.setText(0, 'Monthly')
        irregular_level = QTreeWidgetItem(self.ui.TWmnthVSIrreg)
        irregular_level.setText(0, 'Irregular')
        monthlyIndx = np.where(table[:, tableHead.index('freq')] == 1)
        monthly = table[monthlyIndx]
        for mnth in monthly:
            mnth_item_level = QTreeWidgetItem(monthly_level)
            mnth_item_level.setText(1, mnth[tableHead.index('name')])
            mnth_item_level.setText(2, str(round(mnth[tableHead.index('value')])))

        totalMonthly = table[monthlyIndx,tableHead.index('value')][0]
        monthly_level.setText(1, 'Total')
        monthly_level.setText(2, str(round(sum(totalMonthly), 2)))

        irregIndx = np.where(table[:, tableHead.index('freq')] != 1)
        irregular = table[irregIndx]
        for irr in irregular:
            irr_item_level = QTreeWidgetItem(irregular_level)
            irr_item_level.setText(1, irr[tableHead.index('name')])
            irr_item_level.setText(2, str(round(irr[tableHead.index('value')], 2)))

        totalIrreg = table[irregIndx,tableHead.index('value')][0]
        irregular_level.setText(1, 'Total')
        irregular_level.setText(2, str(round(sum(totalIrreg), 2)))

    def populateExpensesPlan(self, tableHead, table, displayTableHead=None):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        #
        # print(tableHead)
        # print(table)

        if displayTableHead:
            tableHead, table = self.convert_to_display_table(tableHead, table, displayTableHead)

        self.ui.planTable.setColumnCount(len(tableHead))
        self.ui.planTable.setHorizontalHeaderLabels(tableHead)
        self.ui.planTable.setRowCount(table.shape[0])
        for col in range(table.shape[1]):
            for row in range(table.shape[0]):
                if isinstance(table[row, col], int) or isinstance(table[row, col], float):
                    item = QTableWidgetItem()
                    item.setData(QtCore.Qt.DisplayRole, table[row, col])
                elif isinstance(table[row, col], decimal.Decimal):
                    val = float(table[row, col])
                    item = QTableWidgetItem()
                    item.setData(QtCore.Qt.DisplayRole, val)
                else:
                    item = QTableWidgetItem(str(table[row, col]))
                self.ui.planTable.setItem(row, col, item)

        if table.shape[1] > 0:
            self.populate_expenses_summary(tableHead, table)

    def convert_to_display_table(self, tableHead, table, displayTableHead):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        newTableData = np.empty([table.shape[0], len(displayTableHead)], dtype=object)
        for i, col in enumerate(displayTableHead):
            indxCol = tableHead.index(col)
            newTableData[:,i] = table[:, indxCol]

        return displayTableHead, newTableData

    def populate_expenses_summary(self, tableHead, table):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        allValues = table[:, tableHead.index('value')]
        if None in allValues:
            allValues = allValues[allValues != np.array(None)]
        totalVal = round(sum(allValues.astype(float)), 2)
        self.ui.LEtotalNoOfTransactions.setText(str(len(table)))
        self.ui.LEtotalValue.setText(str(totalVal))

        indxMonthly = np.where(table[:,tableHead.index('freq')] == 1)[0]
        monthly = table[indxMonthly, tableHead.index('value')]
        if None in monthly:
            monthly = monthly[monthly != np.array(None)]
        totalMonthly = round(sum(monthly.astype(float)), 2)
        self.ui.LEnoOfMonthly.setText(str(monthly.shape[0]))
        self.ui.LEtotalMonthly.setText(str(totalMonthly))

        indxIrregular = np.where(table[:,tableHead.index('freq')] != 1)[0]
        irregular = table[indxIrregular, tableHead.index('value')]
        if None in irregular:
            irregular = irregular[irregular != np.array(None)]
        totalIrregular = round(sum(irregular.astype(float)), 2)
        self.ui.LEnoOfIrregular.setText(str(irregular.shape[0]))
        self.ui.LEirregular.setText(str(totalIrregular))

    def populateIncomePlan(self, tableHead, table, displayTableHead=None):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        if displayTableHead:
            tableHead, table = self.convert_to_display_table(tableHead, table, displayTableHead)

        self.ui.planTableIncome.setColumnCount(len(tableHead))
        self.ui.planTableIncome.setHorizontalHeaderLabels(tableHead)
        self.ui.planTableIncome.setRowCount(table.shape[0])
        for col in range(table.shape[1]):
            for row in range(table.shape[0]):
                if isinstance(table[row, col], int) or isinstance(table[row, col], float):
                    item = QTableWidgetItem()
                    item.setData(QtCore.Qt.DisplayRole, table[row, col])
                elif isinstance(table[row, col], decimal.Decimal):
                    val = float(table[row, col])
                    item = QTableWidgetItem()
                    item.setData(QtCore.Qt.DisplayRole, val)
                else:
                    item = QTableWidgetItem(str(table[row, col]))
                self.ui.planTableIncome.setItem(row, col, item)

        if table.shape[1] > 0:
            self.populate_income_summary(tableHead, table)

    def populate_income_summary(self, tableHead, table):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        allValues = table[:, tableHead.index('value')]
        if None in allValues:
            allValues = allValues[allValues != np.array(None)]
        # for i in allValues:
        #     print(i, type(i))
        totalVal = sum(allValues.astype(float))
        totalVal = round((totalVal), 2)
        self.ui.LEtotalNoOfIncome.setText(str(len(table)))
        self.ui.LEtotalIncome.setText(str(totalVal))

    def totals(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        if self.ui.LEtotalNoOfTransactions.text():
            expensesTrans = int(self.ui.LEtotalNoOfTransactions.text())
        else:
            expensesTrans = 0
        if self.ui.LEtotalNoOfIncome.text():
            incomeTrans = int(self.ui.LEtotalNoOfIncome.text())
        else:
            incomeTrans = 0

        if self.ui.LEtotalValue.text():
            expenses = float(self.ui.LEtotalValue.text())
        else:
            expenses = 0
        if self.ui.LEtotalIncome.text():
            income = float(self.ui.LEtotalIncome.text())
        else:
            income = 0

        trans = expensesTrans + incomeTrans
        total = round(expenses + income, 2)

        self.ui.LEtotalNo.setText(str(trans))
        self.ui.LEtotalVa.setText(str(total))

    def sortPlan(self, logical_index):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        header = self.ui.planTable.horizontalHeader()
        order = Qt.DescendingOrder
        if not header.isSortIndicatorShown():
            header.setSortIndicatorShown(True)
        elif header.sortIndicatorSection() == logical_index:
            order = header.sortIndicatorOrder()
        header.setSortIndicator(logical_index, order)
        self.ui.planTable.sortItems(logical_index, order)

    def readPlanExpenses(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        rows = self.ui.planTable.rowCount()
        cols = self.ui.planTable.columnCount()
        planExpenseTable = np.empty((rows, cols), dtype=object)
        planExpenseTableHead = []
        for row in range(rows):
            for column in range(cols):
                cell = self.ui.planTable.item(row, column)
                planExpenseTable[row, column] = cell.text()
                colName = self.ui.planTable.horizontalHeaderItem(column).text()
                if colName not in planExpenseTableHead:
                    planExpenseTableHead.append(colName)

        return planExpenseTable, planExpenseTableHead

    def readPlanIncome(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        rows = self.ui.planTableIncome.rowCount()
        cols = self.ui.planTableIncome.columnCount()
        planIncomeTable = np.empty((rows, cols), dtype=object)
        planIncomeTableHead = []
        for row in range(rows):
            for column in range(cols):
                cell = self.ui.planTableIncome.item(row, column)
                planIncomeTable[row, column] = cell.text()
                colName = self.ui.planTableIncome.horizontalHeaderItem(column).text()
                if colName not in planIncomeTableHead:
                    planIncomeTableHead.append(colName)

        return planIncomeTable, planIncomeTableHead

    def plotTablePie(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        realExpenseTable, realExpenseTableHead = self.readPlanExpenses()
        allValues = realExpenseTable[:, realExpenseTableHead.index('value')].astype(float)
        if None in allValues:
            allValues = allValues[allValues != np.array(None)]
        totalVal = sum(allValues)

        colTableName = realExpenseTable[:, realExpenseTableHead.index('table')]
        labels = []
        sizes = []
        for table in np.unique(colTableName):
            indx = np.where(realExpenseTable[:, realExpenseTableHead.index('table')]==table)
            smallArray = realExpenseTable[indx]
            values = sum(smallArray[:, realExpenseTableHead.index('value')].astype(float))
            txt = '{} = {:.2f}'.format(table, values)
            labels.append(txt)
            size = (values/totalVal)*100
            sizes.append(size)

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.2f%%', startangle=90)
        ax1.axis('equal')
        plt.legend(title='Total: {:.2f}'.format(totalVal))

        plt.show()

    def plotNamePie(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        realExpenseTable, realExpenseTableHead = self.readPlanExpenses()
        allValues = realExpenseTable[:, realExpenseTableHead.index('value')].astype(float)
        if None in allValues:
            allValues = allValues[allValues != np.array(None)]
        totalVal = sum(allValues)

        colTableName = realExpenseTable[:, realExpenseTableHead.index('name')]
        labels = []
        sizes = []
        for table in np.unique(colTableName):
            indx = np.where(realExpenseTable[:, realExpenseTableHead.index('name')]==table)
            smallArray = realExpenseTable[indx]
            values = sum(smallArray[:, realExpenseTableHead.index('value')].astype(float))
            txt = '{} = {:.2f}'.format(table, values)
            labels.append(txt)
            size = (values/totalVal)*100
            sizes.append(size)

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.2f%%', startangle=90)
        ax1.axis('equal')
        plt.legend(title='Total: {:.2f}'.format(totalVal))

        plt.show()

    def plotGraf(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        realExpenseTable, realExpenseTableHead = self.readPlanExpenses()
        planIncomeTable, planIncomeTableHead = self.readPlanIncome()
        x_exp = []
        y_exp = []
        for date in np.unique(realExpenseTable[:, realExpenseTableHead.index('payDay')]):
            indx = np.where(realExpenseTable[:, realExpenseTableHead.index('payDay')] == date)
            arr = realExpenseTable[indx, realExpenseTableHead.index('value')].astype(float)
            x_exp.append(date)
            y_exp.append(abs(sum(arr[0])))

        x_inc = []
        y_inc = []
        for date in np.unique(planIncomeTable[:, planIncomeTableHead.index('payDay')]):
            indx = np.where(planIncomeTable[:, planIncomeTableHead.index('payDay')] == date)
            arr = planIncomeTable[indx, planIncomeTableHead.index('value')].astype(float)
            x_inc.append(date)
            y_inc.append(abs(sum(arr[0])))

        fig1, ax1 = plt.subplots()
        ax1.plot(x_exp, y_exp)
        ax1.plot(x_inc, y_inc)
        # plt.setp(plt.get_xticklabels(), rotation=30, ha="right")
        fig1.autofmt_xdate()
        plt.grid()
        plt.show()


def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    # sys.exit(app.exec_())
    app.exec_()


if __name__ == '__main__':
    main()
