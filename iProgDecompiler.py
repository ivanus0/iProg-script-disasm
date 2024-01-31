import os
import sys
from ipr import IPR
from cal import CAL


def decompile_ipr(ipr_filename):
    ipr = IPR(ipr_filename)
    ipr.decompile()
    with open(os.path.splitext(ipr_filename)[0] + '.lst', 'w', encoding='cp1251') as f:
        f.write('\n'.join(ipr.get_lst()))

    decrypted_ipr = ipr.get_ipr()
    if decrypted_ipr:
        with open(os.path.splitext(ipr_filename)[0] + '_decrypted.ipr', 'wb') as f:
            f.write(decrypted_ipr)


def decompile_cal(cal_filename):
    cal = CAL(cal_filename)
    cal.decompile()
    cal_lst = cal.get_lst()
    if cal_lst:
        with open(os.path.splitext(cal_filename)[0] + '.lst', 'w', encoding='cp1251') as f:
            f.write('\n'.join(cal_lst))

    decrypted_cal = cal.get_data()
    if decrypted_cal:
        with open(os.path.splitext(cal_filename)[0] + '_decrypted.bin', 'wb') as f:
            f.write(decrypted_cal)


def decompile(source_filename):
    file_ext = os.path.splitext(source_filename)[1]
    if file_ext == '.ipr':
        decompile_ipr(source_filename)
    elif file_ext == '.cal':
        decompile_cal(source_filename)


if len(sys.argv) > 1:
    filename = sys.argv[1]
    print(f'Processing: {filename}')
    decompile(filename)
else:
    print(sys.argv[0] + ' [script.ipr | calc.cal]')
