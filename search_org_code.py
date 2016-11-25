import os
import functions
import argparse
import xlsxwriter

def get_splitted_string(fragment, indices):
    count = len(indices)
    length = len(fragment)
    all_indices = []
    red_index_list = []

    for idx, value in enumerate(indices):
        # will have 2 numbers that can be used with substring to highlight the match
        positions = value['indices']
        first_pos = positions[0]
        second_pos = positions[1]
        # first index
        if idx == 0:
            temp = fragment[:first_pos]
            if len(temp) > 0:
                all_indices.append(temp)
            all_indices.append(fragment[first_pos:second_pos])
            red_index_list.append(len(all_indices) - 1)
        # last index
        elif idx == count - 1:
            if old_second_pos + 1 != first_pos:
                all_indices.append(fragment[old_second_pos:first_pos])
            all_indices.append(fragment[first_pos:second_pos])
            red_index_list.append(len(all_indices) - 1)
            if (length > second_pos):
                all_indices.append(fragment[second_pos:])
        # in between index
        else:
            if old_second_pos + 1 != first_pos:
                all_indices.append(fragment[old_second_pos:first_pos])
            all_indices.append(fragment[first_pos:second_pos])
            red_index_list.append(len(all_indices) - 1)

        old_second_pos = second_pos

    return {'splitted_string': all_indices, 'red_indices': red_index_list}


def write_sheet_row(worksheet, row, col, fragment, indices):
    red = workbook.add_format({'bold': True, 'color': 'red'})
    normal = workbook.add_format({'text_wrap': True, 'valign': 'top'})

    final_list = []
    string_dict = get_splitted_string(fragment, indices)
    string_list = string_dict['splitted_string']
    red_index_list = string_dict['red_indices']
    for idx, value in enumerate(string_list):
        if idx in red_index_list:
            final_list.append(red)

        final_list.append(value)

    worksheet.write_rich_string(row, col, *final_list)
    worksheet.set_row(row, None, normal)
    worksheet.set_column(col, 1, 100)


cur_path = os.path.dirname(os.path.realpath(__file__))
if (os.name == 'nt'):
    path_seperator = "\\"
else:
    path_seperator = "/"

if os.path.isfile(cur_path + path_seperator + 'local_config.py'):
    import local_config as config
else:
    import config

parser = argparse.ArgumentParser(description='Search all the code repositories from an organization for the given terms and export to an Excel file')
parser.add_argument('--terms', action='append', nargs='+', help='Term(s) to search for')
parser.add_argument('--extension', nargs='?', default="all", help='Extension filter (i.e. py, c, xml), don\'t add a dot.')
parser.add_argument('--excel', nargs=1, help='Excel file name')

search_filter = "user:" + config.Organisation + " in:file"

args = parser.parse_args()
search_terms = args.terms
extension = args.extension
excel_file_name = args.excel[0]

if extension != "all":
    search_filter = search_filter + " extension:" + extension

for term in search_terms[0]:
    search_filter = search_filter + " " + term

# first get all the repositories for your organization
params = { 'q': search_filter }
print ("Going to search for: " + search_filter)
results = functions.do_github_api_request('https://api.github.com/search/code', params, 'get',
                                          [{'Accept': 'application/vnd.github.v3.text-match+json'}])
items = results['items']

workbook = xlsxwriter.Workbook(excel_file_name)
worksheet = workbook.add_worksheet()
bold = workbook.add_format({'bold': True})



worksheet.write('A1', 'Fragment', bold)
worksheet.write('B1', 'Description', bold)
worksheet.write('C1', 'Link', bold)

row = 1
col = 0

for item in items:
    html_url = item['html_url']
    matches = item['text_matches']
    for match in matches:
        fragment = match['fragment']
        height = fragment.count('\n')
        indices = match['matches']
        write_sheet_row(worksheet, row, col, fragment, indices)
        worksheet.write(row, col+2, html_url)
        row += 1

try:
    workbook.close()
    print("File " + excel_file_name + " written!\n")
except IOError:
    print("Can't write file " + excel_file_name + "! Is it still open?\n")
