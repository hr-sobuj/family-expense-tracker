from datetime import datetime
from pathlib import Path
import calendar
import xlsxwriter

def generate_excel(year: int) -> str:
    fixed_expenses = ["WiFi Bill", "Electricity Bill", "House Rent", "Gas Bill", "Others"]
    fixed_income = ["Salary", "Other Income"]  # income fixed items

    output_path = Path(f"/tmp/family_budget_{year}.xlsx")
    workbook = xlsxwriter.Workbook(output_path)

    # Formats
    header_format = workbook.add_format({
        'bold': True, 'bg_color': '#305496', 'font_color': 'white',
        'border': 1, 'align': 'center', 'valign': 'vcenter'
    })
    money_format = workbook.add_format({'num_format': '৳#,##0', 'border': 1})
    default_format = workbook.add_format({'border': 1})
    date_format = workbook.add_format({'num_format': 'dd-mm-yyyy', 'border': 1})
    title_format = workbook.add_format({'bold': True, 'font_size': 14, 'font_color': '#305496'})
    total_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'num_format': '৳#,##0'})

    monthly_totals = {}

    for month_number in range(1, 13):
        month_name = calendar.month_name[month_number]
        worksheet = workbook.add_worksheet(month_name)
        days_in_month = calendar.monthrange(year, month_number)[1]

        worksheet.merge_range('A1:D1', f"{month_name} {year} Expense Tracker", title_format)
        headers = ["Date", "Purpose", "Expense (৳)", "Day"]
        worksheet.set_column('A:D', 18)
        for col, header in enumerate(headers):
            worksheet.write(1, col, header, header_format)

        row = 2
        for day in range(1, days_in_month + 1):
            date_obj = datetime(year, month_number, day)
            worksheet.write_datetime(row, 0, date_obj, date_format)
            worksheet.write(row, 1, "", default_format)  # Purpose
            worksheet.write(row, 2, "", money_format)    # Expense
            worksheet.write(row, 3, date_obj.strftime("%A"), default_format)  # Day
            row += 1

        # Variable Expense total (sum of column C)
        worksheet.write(row, 1, "Variable Expense Total", header_format)
        worksheet.write_formula(row, 2, f"=SUM(C3:C{row})", total_format)

        monthly_totals[month_name] = {
            "variable_expense_total_row": row + 1,  # 1-based
            "fixed_expense_total_row": None,
            "fixed_income_total_row": None,
            "total_expense_row": None,
            "total_saving_row": None,
        }

        start_row = row + 3
        worksheet.write(start_row, 0, "Fixed Monthly Expenses", title_format)
        worksheet.write(start_row + 1, 0, "Item", header_format)
        worksheet.write(start_row + 1, 1, "Amount (৳)", header_format)

        # Write fixed expenses
        fixed_expense_start = start_row + 2
        for i, item in enumerate(fixed_expenses):
            worksheet.write(fixed_expense_start + i, 0, item, default_format)
            worksheet.write(fixed_expense_start + i, 1, "", money_format)

        fixed_expense_total_row = fixed_expense_start + len(fixed_expenses)
        worksheet.write(fixed_expense_total_row, 0, "Fixed Expenses Total", header_format)
        worksheet.write_formula(
            fixed_expense_total_row, 1,
            f"=SUM(B{fixed_expense_start + 1}:B{fixed_expense_total_row})",
            total_format
        )
        monthly_totals[month_name]["fixed_expense_total_row"] = fixed_expense_total_row + 1  # 1-based

        # Fixed Income Section
        income_start = fixed_expense_total_row + 2
        worksheet.write(income_start - 1, 0, "Fixed Monthly Income", title_format)
        worksheet.write(income_start, 0, "Item", header_format)
        worksheet.write(income_start, 1, "Amount (৳)", header_format)

        fixed_income_start = income_start + 1
        for i, item in enumerate(fixed_income):
            worksheet.write(fixed_income_start + i, 0, item, default_format)
            worksheet.write(fixed_income_start + i, 1, "", money_format)

        fixed_income_total_row = fixed_income_start + len(fixed_income)
        worksheet.write(fixed_income_total_row, 0, "Fixed Income Total", header_format)
        worksheet.write_formula(
            fixed_income_total_row, 1,
            f"=SUM(B{fixed_income_start + 1}:B{fixed_income_total_row})",
            total_format
        )
        monthly_totals[month_name]["fixed_income_total_row"] = fixed_income_total_row + 1  # 1-based

        # Total Expense = Variable Expense + Fixed Expenses
        total_expense_row = fixed_income_total_row + 2
        worksheet.write(total_expense_row, 0, "Total Expense (Variable + Fixed)", header_format)
        worksheet.write_formula(
            total_expense_row, 1,
            f"=C{row + 1} + B{fixed_expense_total_row + 1}",
            total_format
        )
        monthly_totals[month_name]["total_expense_row"] = total_expense_row + 1  # 1-based

        # Total Saving = Fixed Income - Total Expense
        total_saving_row = total_expense_row + 1
        worksheet.write(total_saving_row, 0, "Total Saving (Income - Expense)", header_format)
        worksheet.write_formula(
            total_saving_row, 1,
            f"=B{fixed_income_total_row + 1} - B{total_expense_row + 1}",
            total_format
        )
        monthly_totals[month_name]["total_saving_row"] = total_saving_row + 1  # 1-based

    # Yearly Summary Sheet
    summary = workbook.add_worksheet("Yearly Summary")
    summary.merge_range('A1:F1', "Yearly Summary Report", title_format)
    summary_headers = ["Month", "Variable Expense Total", "Fixed Expense Total", "Fixed Income Total", "Total Expense", "Total Saving"]
    summary.set_column('A:F', 25)
    for col, header in enumerate(summary_headers):
        summary.write(1, col, header, header_format)

    for i, (month, rows) in enumerate(monthly_totals.items(), start=2):
        summary.write(i, 0, month, default_format)

        # Variable Expense Total
        summary.write_formula(i, 1, f"='{month}'!C{rows['variable_expense_total_row']}", money_format)

        # Fixed Expense Total
        summary.write_formula(i, 2, f"='{month}'!B{rows['fixed_expense_total_row']}", money_format)

        # Fixed Income Total
        summary.write_formula(i, 3, f"='{month}'!B{rows['fixed_income_total_row']}", money_format)

        # Total Expense
        summary.write_formula(i, 4, f"='{month}'!B{rows['total_expense_row']}", money_format)

        # Total Saving
        summary.write_formula(i, 5, f"='{month}'!B{rows['total_saving_row']}", money_format)

    # Yearly Grand Totals row
    grand_total_row = len(monthly_totals) + 3
    summary.write(grand_total_row, 0, "Yearly Total", header_format)
    summary.write_formula(grand_total_row, 1, f"=SUM(B3:B{grand_total_row})", total_format)
    summary.write_formula(grand_total_row, 2, f"=SUM(C3:C{grand_total_row})", total_format)
    summary.write_formula(grand_total_row, 3, f"=SUM(D3:D{grand_total_row})", total_format)
    summary.write_formula(grand_total_row, 4, f"=SUM(E3:E{grand_total_row})", total_format)
    summary.write_formula(grand_total_row, 5, f"=SUM(F3:F{grand_total_row})", total_format)

    workbook.close()
    return str(output_path)
