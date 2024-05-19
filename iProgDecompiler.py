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
    # filename must be the first argument, otherwise is conflicts with -sn <last num>
    parser = argparse.ArgumentParser(description='Дизассемблер скриптов и калькуляторов iProg',
                                     usage='%(prog)s filename [--bruteforce] | [-sn серийник [серийник ...]]',
                                     add_help=False)
    parser.add_argument('filename', help='Файл скрипта .ipr или файл калькулятора .cal')
    popular_sn = ' '.join(f'{sn}' for sn in Decoder.most_popular_sn)
    parser.add_argument('-sn', nargs='+', type=int, metavar='серийник',
                        help='Использовать эти серийники для раскодирования. '
                             f'Если не указано, пробуем следующие номера: {popular_sn}')
    parser.add_argument('--ignore-check', action='store_true',
                        help='Игнорировать проверку расшифровки и попытаться сохранить как есть')
    parser.add_argument('--bruteforce', action='store_true',
                        help='Поиск sn перебором (возможны ложные срабатывания)')
    parser.add_argument('--brute-all', action='store_true',
                        help='Поиск всех подходящих sn (только для .cal)')

    if sys.argv[1:]:
        args = parser.parse_args()
        return args
    else:
        parser.print_help()
        parser.exit()


def main():
    args = get_args()
    print(f'Processing: {args.filename}')
    if args.sn is not None:
        Decoder.touch(args.sn)
    Decoder.ignore_check = args.ignore_check
    Decoder.bruteforce = args.bruteforce
    Decoder.brute_all = args.brute_all
    decompile(args.filename)


main()
