__author__ = 'baez'
import datetime
import ftplib
import numpy as np
import pandas as pd


def get_data_types(ftp_user, ftp_passwd):

    ftp = ftplib.FTP("arthurhou.pps.eosdis.nasa.gov", timeout=600)
    ftp.login(ftp_user, ftp_passwd)
    main_dir = '/pub/gpmdata'
    ftp.cwd(main_dir)
    years = []
    ftp.dir(years.append)
    years = [year.split()[-1] for year in years]
    years = [year for year in years if year.isdigit()]

    one_C = {}
    imerg = {}
    products_list = []
    for year in years:
        dir_y = main_dir + "/" + year + "/"
        ftp.cwd(dir_y)
        months = []
        ftp.dir(months.append)
        months = [month.split()[-1] for month in months]
        for month in months:
            dir_ym = dir_y + month + "/"
            ftp.cwd(dir_ym)
            days = []
            ftp.dir(days.append)
            days = [day.split()[-1] for day in days]
            for day in days:
                dir_ymd = dir_ym + day + "/"
                print year, month, day
                ftp.cwd(dir_ymd)
                products = []
                ftp.dir(products.append)
                product = [year, month, day] + [l.split()[-1] for l in products]
                products_list.append(product)
                if "1C" in product:
                    ftp.cwd(dir_ymd + "1C/")
                    data = []
                    ftp.dir(data.append)
                    one_C[(year, month, day)] = [l.split("/")[-1] for l in data]
                elif "imerg" in product:
                    ftp.cwd(main_dir + "/" + year + "/" + month + "/" + day + "/" + "imerg/")
                    data = []
                    ftp.dir(data.append)
                    imerg[(year, month, day)] = [l.split("/")[-1] for l in data]
                if '2007/01/06' in dir_ymd:
                    break
            if '2007/01/06' in dir_ymd:
                break
        if '2007/01/06' in dir_ymd:
            break
    ftp.close()
    print one_C
    return
    products = set()
    for p in products_list:
        products = products.union(p[3:])
    columns = sorted(list(products))
    df = pd.DataFrame(columns=columns)
    for p in products_list:
        p1 = p[3:]
        df.loc[datetime.datetime.strptime('-'.join(p[:3]), '%Y-%m-%d')] = [(c in p1) for c in columns]
    df.to_csv("D:/Temp/test.csv", sep=';', index_label='Date')
    # np.savetxt("D:/Baez/Baez/doctorado/Materias/Flood Management/1C_files.txt", np.array(one_C), fmt="%s")
    # np.savetxt("D:/Baez/Baez/doctorado/Materias/Flood Management/imerg_files.txt", np.array(imerg), fmt="%s")


# get_data_types("oscarmbaez89@hotmail.com", "oscarmbaez89@hotmail.com")