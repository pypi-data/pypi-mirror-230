import os.path

import pandas as pd
import ujson
from flatten_everything import flatten_everything
from operagxdriver import start_opera_driver
import re
import time
from a_selenium_scroll_down_forever import scroll_down_forever

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from a_selenium2df import get_df
from PrettyColorPrinter import add_printer

add_printer(1)
from a_pandas_ex_plode_tool import pd_add_explode_tools
from a_selenium_add_special_keys import add_special_keys
from get_consecutive_filename import get_free_filename

pd_add_explode_tools()


def parse_artists(
    allplaylists,
    savefolder,
    opera_browser_exe,
    opera_driver_exe,
    userdir,
):
    r"""

    Args:
        allplaylists (list): A list of Spotify playlist URLs to scrape data from.
        savefolder (str): The folder where the scraped data will be saved as Excel files.
        opera_browser_exe (str): The path to the Opera GX browser executable.
        opera_driver_exe (str): The path to the Opera WebDriver executable.
        userdir (str): The path to the user directory for the Opera browser.
    
    Returns:
        None: The scraped data is saved as Excel files in the specified 'savefolder'.
    
    Example Usage:
        parse_artists(
            allplaylists=[
                'https://open.spotify.com/playlist/3DBZUCUA2w8JcE8mBA0wUB',
                'https://open.spotify.com/playlist/37i9dQZF1DWZLiXDryu4Fe',
                'https://open.spotify.com/playlist/6DSfG4qBWdpaNK9PclUeAI',
                'https://open.spotify.com/playlist/37i9dQZF1DXdSjVZQzv2tl',
                'https://open.spotify.com/playlist/1XhfOTC9d3VwyJrS3EW8iW'
            ],
            savefolder="c:\\savedmusic",
            opera_browser_exe=r"C:\Program Files\Opera GX\opera.exe",
            opera_driver_exe=r"C:\ProgramData\anaconda3\envs\dfdir\operadriver.exe",
            userdir="c:\\operabrowserprofile2"
        )
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
    driver = add_special_keys(driver)

    if not os.path.exists(savefolder):
        os.makedirs(savefolder)

    for oneplaylist in allplaylists:
        try:
            driver.get(oneplaylist)
            time.sleep(2)
            for ta in range(20):
                driver.send_PageDown_key()
                time.sleep(0.1)
            dfx = g()
            artists = dfx.loc[
                dfx.aa_innerHTML.str.contains("/track/", na=False, regex=False)
                & dfx.aa_firstElementChild.str.contains(
                    "/track/", na=False, regex=False
                )
            ][["aa_innerText", "aa_firstElementChild"]]
            df4 = pd.concat(
                [
                    artists.aa_innerText.str.split("\n", n=1, expand=True)
                    .reset_index(drop=True)
                    .rename(columns={0: "aa_song", 1: "aa_artist"}),
                    artists["aa_firstElementChild"].reset_index(drop=True),
                ],
                axis=1,
            )
            for key111, item111 in df4.iterrows():
                try:
                    driver.get(
                        "https://huggingface.co/spaces/Longliveruby/Spotify-Recommendation-System"
                    )
                    df2 = pd.DataFrame()
                    df = pd.DataFrame()
                    time.sleep(1)
                    while df2.empty:
                        try:
                            df = g("button,input")
                            df2 = df.loc[
                                (df.aa_localName == "input") & (df.aa_type == "radio")
                            ]  # .iloc[-1]
                            if len(df2) < 6:
                                df2 = pd.DataFrame()
                        except Exception as fe:
                            print(fe)
                    df2.iloc[-1].js_click()
                    time.sleep(1)
                    df2.iloc[1].js_click()
                    time.sleep(1)
                    df = g("button,input,a")
                    df2 = df.loc[(df.aa_localName == "input")]
                    df2.iloc[-1].se_send_keys(
                        f"{item111['aa_firstElementChild'].strip()}\n"
                    )
                    df2 = df.loc[
                        (df.aa_localName == "button")
                        & (df.aa_innerHTML == "Get Recommendations")
                    ]
                    df2.iloc[0].js_click()
                    time.sleep(2)
                    df2 = df.loc[
                        (df.aa_localName == "a") & (df.aa_innerText == "Result")
                    ]
                    df2.iloc[0].js_click()
                    time.sleep(2)
                    scroll_down_forever(
                        driver,
                        pause_between_scrolls=(0.5, 1),
                        max_scrolls=3,
                        timeout=3,
                        script_timeout=1,
                    )
                    df = g("script")
                    try:
                        parseddata = df.loc[
                            (df.aa_id == "__NEXT_DATA__")
                        ].aa_text.to_list()
                    except Exception as fe:
                        # print(fe)
                        parseddata = [
                            q
                            for q in df.aa_text.dropna().to_list()
                            if str(q).startswith('{"props"')
                        ]

                    allp = [
                        pd.Q_AnyNestedIterable_2df(ujson.loads(data), unstack=True)
                        for data in parseddata
                    ]
                    finaldf = pd.concat(
                        [
                            df.loc[df.aa_all_keys.apply(lambda x: "strings" not in x)]
                            .assign(
                                cate=lambda h: h.aa_all_keys.apply(
                                    lambda r: "_".join(
                                        list([str(hh) for hh in flatten_everything(r)])
                                    )
                                )
                            )[["cate", "aa_value"]]
                            .set_index("cate")
                            .T
                            for df in allp
                        ]
                    ).copy()
                    finaldf.columns = [
                        re.sub(r"\W+", "", "aa_" + re.sub("_+", "_", x).strip(" _"))
                        for x in finaldf.columns
                    ]
                    for col in df4.columns:
                        finaldf[col] = item111[col]

                    fname = get_free_filename(
                        folder=savefolder, fileextension=".xlsx", leadingzeros=8
                    )
                    print(fname)
                    finaldf.to_excel(fname)

                except Exception as fea:
                    print(fea)
                    continue

        except Exception as fax:
            print(fax)
            continue
