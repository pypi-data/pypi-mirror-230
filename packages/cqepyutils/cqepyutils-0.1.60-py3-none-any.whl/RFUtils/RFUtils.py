from robot.api import ExecutionResult, ResultVisitor
import csv
import pandas as pd


def email_trigger(xml_file, csv_file, html_file):
    class TestMetrics(ResultVisitor):

        def visit_test(self, test):
            wr.writerow([test.name, test.doc, test.status, test.message, test.elapsedtime / float(1000)])

    class SuiteMetrics(ResultVisitor):

        def visit_suite(self, suite):
            stats = result.suite.statistics
            wr1.writerow(
                [suite.name, suite.status, stats.total, stats.passed, stats.failed, suite.elapsedtime / float(60000)])

    op_f = open(csv_file, 'w')
    wr = csv.writer(op_f)

    wr.writerow(['TESTCASE_NAME', 'DOCUMENTATION', 'TESTCASE_STATUS', 'FAILURE_ANALYSIS', 'TESTCASE_ELAPSEDTIME'])
    result = ExecutionResult(xml_file)
    print('after result')
    result.visit(TestMetrics())
    op_f.close()

    suite_csv = csv_file.replace('.csv', '_suite.csv')
    op_f1 = open(suite_csv, 'w')
    wr1 = csv.writer(op_f1)
    wr1.writerow(['SUITE_NAME', 'SUITE_STATUS', 'TOTAL_TESTCASES', 'TESTCASES_PASSED', 'TESTCASES_FAILED',
                  'EXECUTION_TIME'])

    result.visit(SuiteMetrics())
    op_f1.close()
    csv_to_html(csv_file, suite_csv, html_file, 'TESTCASE_STATUS')


def csv_to_html(csv_file, suite_csv, html_file, highlight_column_name):
    df = pd.read_csv(csv_file, index_col=False)
    df = df[~df.TESTCASE_NAME.str.contains("Placeholder Test")]
    df.fillna('', inplace=True)
    print(df)

    df1 = pd.read_csv(suite_csv, index_col=False)
    print(df1)

    html = df.style.applymap(highlight_vals, subset=[highlight_column_name]).\
        applymap(center_vals, subset=['TESTCASE_STATUS']).\
        applymap(center_vals, subset=['TESTCASE_ELAPSEDTIME']).\
        applymap(left_vals, subset=['DOCUMENTATION']).set_table_styles(
        [{'selector': 'tr.hover td', 'props': [('background-color', 'lightyellow')]},
         {'selector': 'th, td', 'props': [('border', '1px solid black'),
                                          ('padding', '14px'), ('text-align', 'left')]},
         {'selector': 'th', 'props': [('font-family', 'Century Gothic'), ('font-size', '9pt')]},
         {'selector': 'thead', 'props': [('background-color', 'lightblue')]},
         {'selector': '', 'props': [('border-collapse', 'collapse'),
                                    ('border', '1px solid black')]},
         ]).set_properties(**{'font-size': '10pt', 'font-family': 'Century Gothic'}).render()
    html = html.replace('<th class="blank level0 ></th>', '<th class="blank level0">S_NO</th>')

    html1 = df1.style.applymap(highlight_cols_red, subset=['TESTCASES_FAILED']).\
        applymap(center_vals, subset=['SUITE_STATUS']).\
        applymap(center_vals, subset=['TOTAL_TESTCASES']). \
        applymap(center_vals, subset=['TESTCASES_PASSED']). \
        applymap(center_vals, subset=['TESTCASES_FAILED']).set_table_styles(
        [{'selector': 'tr.hover td', 'props': [('background-color', 'lightyellow')]},
         {'selector': 'th, td', 'props': [('border', '1px solid black'),
                                          ('padding', '4px'), ('text-align', 'left')]},
         {'selector': 'th', 'props': [('font-family', 'Century Gothic'), ('font-size', '9pt')]},
         {'selector': 'thead', 'props': [('background-color', 'lightblue')]},
         {'selector': '', 'props': [('border-collapse', 'collapse'),
                                    ('border', '1px solid black')]},
         ]).set_properties(**{'font-size': '10pt', 'font-family': 'Century Gothic'}).render()
    html1 = html1.replace('<th class="blank level0 ></th>', '<th class="blank level0">S_NO</th>')

    html_content = html1 + "<b>Automation Execution Detailed Summary:</br></br>" + html
    with open(html_file, 'w') as f:
        f.write(html_content)
    f.close()


def highlight_vals(val, color='lightgreen'):
    if val == 'PASS':
        return 'background-color: %s' % color
    else:
        return 'background-color: red'


def center_vals(val):
    return 'text-align: center'


def highlight_cols_green(val, color='lightgreen'):
    return 'background-color: %s' % color


def highlight_cols_red(val, color='red'):
    return 'background-color: %s' % color


def left_vals(val):
    return 'text-align: left'

