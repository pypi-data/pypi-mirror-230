import chelt_plan_new
from mysqlquerys import connect
from datetime import date


def main():
    ini_file = r"D:\Python\MySQL\database.ini"
    selectedStartDate = date(2021, 12, 30)
    selectedEndDate = date(2024, 1, 29)

    # app = chelt_plan.CheltuieliPlanificate()
    # all_chelt = app.get_all_sql_vals()
    # app.filter_dates(all_chelt, selectedStartDate, selectedEndDate)
    # app.prepareTablePlan('all', selectedStartDate, selectedEndDate)
    table = connect.Table(ini_file, 'cheltuieli', 'income')
    row = table.returnRowsWhere(('id', 1))[0]
    print(row)
    # chelt = chelt_plan_new.Cheltuiala(row, table.columnsNames)
    # ff = chelt.calculate_payments_in_interval(selectedStartDate, selectedEndDate)
    # print('µµµµµµ', ff)
    # # print(type(ff))

    venit_instance = chelt_plan_new.Income(list(row), table.columnsNames)
    value = venit_instance.calculate_income()
    print(value)

if __name__ == '__main__':
    main()
