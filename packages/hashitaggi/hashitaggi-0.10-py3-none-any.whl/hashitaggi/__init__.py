import random
from operagxdriver import start_opera_driver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from a_selenium2df import get_df
from PrettyColorPrinter import add_printer
add_printer(1)
from kthread_sleep import sleep
import pandas as pd
import ujson
from a_pandas_ex_plode_tool import pd_add_explode_tools
pd_add_explode_tools()


def get_hashtags(
    hashtags,
    opera_browser_exe,
    opera_driver_exe,
    userdir,
):
    r"""
    This function, `get_hashtags`, scrapes and processes data from the Display Purposes website to retrieve information
    about hashtags. It returns a DataFrame containing relevant information about the hashtags, including their rankings.

    Parameters:
        hashtags (list): A list of hashtags to retrieve information for.
        opera_browser_exe (str): The file path to the Opera GX browser executable.
        opera_driver_exe (str): The file path to the Opera WebDriver executable.
        userdir (str): The directory path for the Opera browser user profile.

    Returns:
        pandas.DataFrame: A DataFrame containing information about the hashtags, including their rankings.

    Example:
        from hashitaggi import get_hashtags
        df = get_hashtags(
            hashtags=['jiujitsu', 'bjj'],
            opera_browser_exe=r"C:\Program Files\Opera GX\opera.exe",
            opera_driver_exe=r"C:\ProgramData\anaconda3\envs\dfdir\operadriver.exe",
            userdir=r"C:\operabrowserprofile2",
        )
        print(df)
    """

    def g(q="*"):
        return get_df(
            driver,
            By,
            WebDriverWait,
            expected_conditions,
            queryselector=q,
            with_methods=True,
        )

    driver = start_opera_driver(
        opera_browser_exe=opera_browser_exe,
        opera_driver_exe=opera_driver_exe,
        userdir=userdir,
        arguments=(
            "--no-sandbox",
            "--test-type",
            "--no-default-browser-check",
            "--no-first-run",
            "--incognito",
            "--start-maximized",
            "--headless",
        ),
    )

    hashis = [str(x) for x in hashtags]
    allframes = []
    for hashtag in hashis:
        try:
            driver.get(
                f'https://displaypurposes.com/hashtags/hashtag/{hashtag.split("/")[-1].strip(" #")}'
            )
            sleep(random.uniform(3, 8))
            df = g(q="*")
            for t in (
                df.loc[df.aa_localName == "script"]
                .dropna(subset="aa_innerHTML")
                .aa_innerText
            ):
                try:
                    df2 = pd.Q_AnyNestedIterable_2df((ujson.loads(t)), unstack=True)
                    df2["aa_all_keys"] = df2["aa_all_keys"].apply(lambda x: x[:-2])
                except Exception as fe:
                    print(fe)
                    continue
            alltags = []
            for name, group in df2.groupby(["aa_all_keys", "level_3"]):
                if len(group) == 2:
                    if isinstance(group.aa_value.iloc[-1], int):
                        group2 = group.loc[group.level_2 == "rank"]
                        if not group2.empty:
                            alltags.append(
                                group2.sort_values(by="level_4").aa_value.to_list()
                            )
            alltafs = pd.DataFrame(alltags).drop_duplicates().reset_index(drop=True)
            allframes.append(alltafs.copy())
        except Exception as fe:
            print(fe)
            continue
    try:
        driver.close()
    except Exception:
        pass
    try:
        driver.quit()
    except Exception:
        pass
    try:
        if len(allframes) == 1:
            return (
                allframes[0]
                .drop_duplicates()
                .sort_values(by=1, ascending=False)
                .reset_index(drop=True)
            )
        return (
            pd.concat(allframes)
            .drop_duplicates()
            .sort_values(by=1, ascending=False)
            .reset_index(drop=True)
        )
    except Exception as fe:
        print(fe)
    return pd.DataFrame()




