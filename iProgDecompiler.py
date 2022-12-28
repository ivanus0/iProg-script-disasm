import os
import sys
from ipr import IPR
from cal import CAL


def decompile_ipr(ipr_filename):
    ipr = IPR(ipr_filename)
    ipr.decompile()
    with open(os.path.splitext(ipr_filename)[0] + '.lst', 'w') as f:
        f.write('\n'.join(ipr.get_lst()))
        f.close()

    with open(os.path.splitext(ipr_filename)[0] + '_decrypted.ipr', 'wb') as f:
        f.write(ipr.get_ipr())
        f.close()


def decompile_cal(cal_filename):
    cal = CAL(cal_filename)
    cal.decompile()
    with open(os.path.splitext(cal_filename)[0] + '.lst', 'w') as f:
        f.write('\n'.join(cal.get_lst()))
        f.close()

    with open(os.path.splitext(cal_filename)[0] + '_decrypted.cal', 'wb') as f:
        f.write(cal.get_data())
        f.close()


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
