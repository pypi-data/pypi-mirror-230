import pdb
import logging
import platform
import undetected_chromedriver as uc
from selenium import webdriver
from ladderbot.gui import show_gui
from ladderbot import controllers
import importlib.resources
#-----------------------------------------------
def bot():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=str(importlib.resources.files("ladderbot")) + "\\debug.log",
        filemode='w'
    )
    # Create logger
    logger = logging.getLogger()
    show_gui()
    chrome_options = uc.ChromeOptions()
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    chrome_options.add_argument("--window-position=-5,695")
    chrome_options.add_experimental_option("prefs", prefs)
    platform_name = platform.system()
    logger.info(f"Running on {platform_name}")
    while True:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(900, 705)
        login = controllers.LoginController(driver, logger)
        # run the login routine now so the rest the controllers can gather game data as they initialize
        login.run(character_name='MrParachute')
        player_controller = controllers.PlayerController(driver, logger)
        leveler = controllers.LevelingController(driver, logger)
        navigator = controllers.NavigationController(driver, logger)
        inventory = controllers.InventoryController(driver, logger)
        transmuter = controllers.TransmuteController(driver, logger)
        tranfer_controller = controllers.TransferController(driver, logger)
        # market = controllers.MarketController(driver, logger, gold_password='temp')
        vault = controllers.VaultController(driver, logger)
        player = controllers.Player(logger, player_controller, leveler, inventory, navigator, vault, transmuter, tranfer_controller)
        player.run()
#-----------------------------------------------