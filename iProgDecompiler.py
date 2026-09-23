import argparse
import os
import sys
from decode import Decoder
from ipr import IPR
from cal import CAL


def decompile_ipr(ipr_filename, extra):
    ipr = IPR(ipr_filename)
    ipr.decompile(extra)
    with open(os.path.splitext(ipr_filename)[0] + '.lst', 'w', encoding='cp1251') as f:
        f.write('\n'.join(ipr.get_lst()))

    with open(os.path.splitext(ipr_filename)[0] + '_draft.blr', 'w', encoding='cp1251') as f:
        f.write('\n'.join(ipr.get_draft()))

    if ipr.cypher:
        decrypted_ipr = ipr.get_ipr()
        if decrypted_ipr:
            with open(os.path.splitext(ipr_filename)[0] + '_decrypted.ipr', 'wb') as f:
                f.write(decrypted_ipr)


def decompile_cal(cal_filename, extra):
    cal = CAL(cal_filename)
    cal.decompile(extra)
    cal_lst = cal.get_lst()
    if cal_lst:
        with open(os.path.splitext(cal_filename)[0] + '.lst', 'w', encoding='cp1251') as f:
            f.write('\n'.join(cal_lst))

    decrypted_cal = cal.get_data()
    if decrypted_cal:
        # with open(os.path.splitext(cal_filename)[0] + '_decrypted.bin', 'wb') as f:
        #     f.write(decrypted_cal)
        sn = extra.get('newsn')
        if sn is not None:
            with open(f'{os.path.splitext(cal_filename)[0]}_{sn:05}.cal', 'w') as f:
                f.write(Decoder.encode_cal_bytecode(decrypted_cal, sn))


def decompile_file(source_filename, args):
    if not os.path.isfile(source_filename):
        print(f'No such file: {source_filename}')
        return False

    file_ext = os.path.splitext(source_filename)[1].lower()

    try:
        print(f'Processing: {source_filename}')

        if file_ext == '.ipr':
            extra = {
                'eph': args.eph,
                'epd': args.epd,
            }
            decompile_ipr(source_filename, extra)

        elif file_ext == '.cal':
            extra = {
                'eph': args.eph,
                'newsn': args.newsn,
            }
            decompile_cal(source_filename, extra)

        else:
            print(f'Skipped: unsupported extension "{file_ext}"')
            return False

        print(f'OK: {source_filename}')
        return True

    except Exception as exc:
        print(f'ERROR: {source_filename}')
        print(f'  {type(exc).__name__}: {exc}')
        return False


def collect_files(path, recursive=False):
    path = os.path.abspath(path)

    if os.path.isfile(path):
        return [path]

    if not os.path.isdir(path):
        return []

    found = []

    if recursive:
        for root, _, files in os.walk(path):
            for name in files:
                if os.path.splitext(name)[1].lower() in ('.ipr', '.cal'):
                    found.append(os.path.join(root, name))
    else:
        for name in os.listdir(path):
            full = os.path.join(path, name)
            if os.path.isfile(full) and os.path.splitext(name)[1].lower() in ('.ipr', '.cal'):
                found.append(full)

    return sorted(found, key=lambda p: p.lower())


def decompile(source_filename, args):
    if os.path.isfile(source_filename):
        return decompile_file(source_filename, args)

    if os.path.isdir(source_filename):
        files = collect_files(source_filename, args.recursive)

        if not files:
            print(f'No .ipr or .cal files found in: {source_filename}')
            return False

        print(f'Found {len(files)} file(s) in: {source_filename}')
        if args.recursive:
            print('Recursive mode: ON')

        ok = 0
        failed = 0

        for filename in files:
            print('-' * 72)
            if decompile_file(filename, args):
                ok += 1
            else:
                failed += 1

        print('=' * 72)
        print('Batch finished')
        print(f'OK     : {ok}')
        print(f'Failed : {failed}')
        print(f'Total  : {len(files)}')
        return failed == 0

    print(f'No such file or directory: {source_filename}')
    return False


def get_args():

    def check_serial(sn):
        if sn.isdigit():
            v = int(sn)
            if 0 <= v <= 65535:
                return v
            else:
                raise argparse.ArgumentTypeError(
                    f'недопустимый серийник {v}, должно быть от 0 до 65535'
                )
        raise argparse.ArgumentTypeError(
            f'неверный серийник "{sn}", должно быть число'
        )

    def check_serials(s: str):
        result = []
        for r in s.split(','):
            mm = r.split('-', maxsplit=1)
            f = check_serial(mm[0])
            if len(mm) == 2:
                t = check_serial(mm[1])
                if f > t:
                    f, t = t, f
                if f != t:
                    result.append(range(f, t + 1))
                    continue
            result.append(f)
        return result

    parser = argparse.ArgumentParser(
        description='Дизассемблер скриптов и калькуляторов iProg. '
                    'Без имени файла обрабатывает все .ipr/.cal в папке скрипта.',
        usage='%(prog)s [filename|directory] [options]'
    )

    parser.add_argument(
        'filename',
        nargs='?',
        default=None,
        help='Файл .ipr/.cal или папка. '
             'Если не указано — папка, где находится iProgDecompiler.py'
    )

    popular_sn = ','.join(f'{sn}' for sn in Decoder.most_popular_sn)

    parser.add_argument(
        '-sn',
        type=check_serials,
        metavar='серийники',
        help='Использовать эти серийники для раскодирования. Через "," или диапазоны через "-". '
             f'Если не указано, пробуем следующие номера: {popular_sn}'
    )

    parser.add_argument(
        '--bruteforce',
        action='store_true',
        help='Поиск sn перебором (возможны ложные срабатывания). То же, что -sn 0-65535'
    )

    parser.add_argument(
        '--brute-quick',
        action='store_true',
        help='Быстрая проверка (возможны ложные срабатывания)'
    )

    parser.add_argument(
        '--newsn',
        type=check_serial,
        metavar='серийник',
        help='Сохранить с новым серийником (только для .cal)'
    )

    parser.add_argument(
        '--brute-all',
        action='store_true',
        help='Поиск всех подходящих sn (только для .cal)'
    )

    parser.add_argument(
        '--ignore-check',
        action='store_true',
        help='Игнорировать проверку расшифровки и попытаться сохранить как есть'
    )

    parser.add_argument(
        '--eph',
        type=lambda a: (int(i, 0) for i in a.split(',')),
        help='host ep (and for .cal)'
    )

    parser.add_argument(
        '--epd',
        type=lambda a: (int(i, 0) for i in a.split(',')),
        help='device ep'
    )

    parser.add_argument(
        '-r',
        '--recursive',
        action='store_true',
        help='Для папки обрабатывать также все подпапки'
    )

    args = parser.parse_args()

    if args.filename is None:
        args.filename = os.path.dirname(os.path.abspath(__file__))

    return args


def main():
    args = get_args()
    Decoder.init_args(args)
    decompile(args.filename, args)


if __name__ == '__main__':
    main()
