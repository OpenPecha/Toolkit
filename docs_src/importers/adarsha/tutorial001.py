from openpecha.formatters.adarsha import parse_pecha

#work = [pecha_name,pbs]
work = ['bonpokangyur', 2426116]
output_path = "tests/formatters/adarsha/data"

parse_pecha(output_path,work)
