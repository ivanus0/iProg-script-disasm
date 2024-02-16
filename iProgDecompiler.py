import argparse
import os
import sys
from decode import Decoder
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
    if os.path.isfile(source_filename):
        file_ext = os.path.splitext(source_filename)[1]
        if file_ext == '.ipr':
            decompile_ipr(source_filename)
        elif file_ext == '.cal':
            decompile_cal(source_filename)
    else:
        print('No such file')


def get_args():
    parser = argparse.ArgumentParser(description='Дизассемблер скриптов и калькуляторов iProg')
    parser.add_argument('filename', help='файл скрипта .ipr или файл калькулятора .cal')
    popular_sn = ', '.join(f'"{sn}"' for sn in Decoder.most_popular_sn)
    parser.add_argument('-sn', nargs='+', type=int, metavar='серийник',
                        help='использовать эти серийники для раскодирования, '
                             f'если не указано, пробуем следующие номера: {popular_sn}'
                        )
    parser.add_argument('--ignore-check',
                        help='игнорировать проверку расшифровки и попытаться сохранить как есть', action='store_true')
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    return args


def main():
    args = get_args()
    print(f'Processing: {args.filename}')
    if args.sn is not None:
        Decoder.touch(args.sn)
    if args.ignore_check:
        Decoder.ignore_check = args.ignore_check
    decompile(args.filename)


main()
