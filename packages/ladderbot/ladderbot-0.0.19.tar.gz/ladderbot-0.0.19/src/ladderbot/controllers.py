# import os
import pdb
import math
import pandas as pd
import importlib.resources
from time import sleep
from random import choice, randint
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from ladderbot.items import Weapon, Armor, Charm
from ladderbot.mappings import transmute_mapping, item_pickup_mapping, desireable_stats_mapping, prices
#-----------------------------------------------
class LoginController:
    def __init__(self, driver, logger) -> None:
        self.name = "LoginController"
        self.logger = logger
        self.driver = driver
    def run(self, character_name:str):
        # self.controller.login()
        # launch the game
        self.start_game()
        current_location = self.check_location()
        if current_location == 'catacombs':
            self.leave_cata()
            self.logout_character()
            self.select_character(character_name)
        # already at the town
        elif current_location == 'town':
            # logout current character
            self.logout_character()
            self.select_character(character_name)
        # login desired character
        elif current_location == 'character_selection':
            self.select_character(character_name)
            if self.check_location() == 'character_creation':
                class_options_container = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'ccClassList'))
                )
                class_option_elements = WebDriverWait(class_options_container, 5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'njRB'))
                )
                desired_class_element = class_option_elements[-1]
                desired_class_element.click()
                submit_button_element = class_options_container = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'ccSubmit'))
                )
                submit_button_element.click()
                self.select_character(character_name)
    def check_location(self) -> bool:
        self.logger.info(f"{self.name}.check_location() --> Reading player location")
        indicators = {
            'town' : (By.CLASS_NAME, 'townOIcon'),
            'catacombs' : (By.CLASS_NAME, 'bgCata'),
            'pond' : (By.XPATH, '//*[@id="bg"]/img'),
            'character_selection' : (By.XPATH, '//*[@id="bg"]/div[1]/a'),
            'character_selected' : (By.XPATH, '//*[@id="bg"]/div[2]/div/a[2]'),
            'character_creation' : (By.CLASS_NAME, 'ccSubmit'),
        }
        for location in indicators:
            try:
                WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located(indicators.get(location))
                )
                self.logger.info(f"{self.name}.check_location() --> {location=}")
                return location
            except Exception as e:
                pass
        else:
            self.logger.error(f"{self.name}.check_location() --> Location Unknown!")
            return False
    def leave_cata(self):
        self.logger.info(f"{self.name}.leave_cata() --> Leaving Catacombs")
        # Spams exiting the catacombs until we've left
        while self.check_location() == 'catacombs':
            try:
                to_town_button = self.driver.find_element(By.CLASS_NAME, "gradRed")
                # to_town_button.click()
                self.driver.execute_script("arguments[0].click();", to_town_button)
            except Exception as e:
                # Failed to leave catacombs, keep trying forever. or die...
                pass
    def start_game(self):
        html_file = Path(str(importlib.resources.files("ladderbot")) + "\\index.html")
        play_url = html_file.as_uri()
        self.logger.info(f"{self.name}.start_game() --> Starting Game {play_url=}")
        self.driver.get(play_url)
        try: 
            play_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'abutGradBl'))
            )
            # play_button.click()
            self.driver.execute_script("arguments[0].click();", play_button)
        except TimeoutError as e:
            raise e
        try: 
            stage = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, 'stage'))
            )
            # stage.click()
            self.driver.execute_script("arguments[0].click();", stage)
        except TimeoutError as e:
            raise e
    def select_character(self, name:str):
        self.logger.info(f"{self.name}.select_character() --> {name=}")
        character_list = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'charList'))
        )
        available_characters = character_list.find_elements(By.CLASS_NAME, 'cName')
        character = list(filter(lambda x:x.text == name, available_characters))[0]
        # character.click()
        self.driver.execute_script("arguments[0].click();", character)
        character_play_button = self.driver.find_element(By.CLASS_NAME, 'clPlay')
        # character_play_button.click()
        self.driver.execute_script("arguments[0].click();", character_play_button)
    def logout_character(self):
        self.logger.info(f"{self.name}.logout_character()")
        button_grouping = self.driver.find_element(By.CLASS_NAME, 'ctrlButtons')
        logout_character_button = button_grouping.find_elements(By.TAG_NAME, 'img')[-1]
        # logout_character_button.click()
        self.driver.execute_script("arguments[0].click();", logout_character_button)
#-----------------------------------------------
class InventoryController:
    def __init__(self, driver, logger) -> None:
        self.name = "InventoryController"
        self.driver = driver
        self.logger = logger
        self.action = ActionChains(self.driver)
        self.weapon = None
        self.armor = None
        self.charm = None
        self.acc_charm = None
        self.equipment = None
    def load(self):
        self.weapon, self.armor, self.charm, self.acc_charm = self.load_equipped_items()
        self.equipment = self.load_equipment()
        self.close_all()
    def is_full(self):
        equipment_count = self.get_equipment_count()
        return equipment_count[0] == equipment_count[1]
    def open(self):
        self.action.send_keys(Keys.SPACE).perform()
        self.action.send_keys("i").perform()
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'pbInv'))
            )
        except TimeoutError as e:
            raise e
    def close_all(self):
        self.action.send_keys(Keys.SPACE).perform()
    def get_equipment_count(self):
        self.logger.info(f"{self.name} --> getting inventory capacity")
        self.open()
        equipment_label_element = WebDriverWait(self.driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'invEqCountLabel'))
        )
        label_text = equipment_label_element.text
        current, capacity = [int(letter) for letter in label_text.split() if letter.isdigit()]
        self.logger.info(f"{self.name} --> {current=}, {capacity=}")
        self.close_all()
        return current, capacity
    def load_equipped_items(self):
        self.logger.info(f"{self.name} --> reading equipped items from inventory")
        self.open()
        equipped_items_container = WebDriverWait(self.driver, .5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'invEquipped'))
        ) 
        equipped_items = WebDriverWait(equipped_items_container, .5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'itemSlotBox'))
        )
        weapon, armor, charm, acc_charm = equipped_items
        item_tier = weapon.text.replace('+',"").split('\n')[-1]
        self.action.move_to_element(weapon).perform()
        try:
            weapon_stats_popup = WebDriverWait(self.driver, .5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'tbItemDesc'))
            )
            weapon = Weapon(weapon_stats_popup, item_tier)
        except TimeoutException:
            self.logger.info(f"{self.name} --> TimeoutException: weapon not equipped")
            weapon = None
        item_tier = armor.text.replace('+',"").split('\n')[-1]
        self.action.move_to_element(armor).perform()
        try:
            armor_stats_popup = WebDriverWait(self.driver, .5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'tbItemDesc'))
            )
            armor = Armor(armor_stats_popup, item_tier)
        except TimeoutException:
            self.logger.info(f"{self.name} --> TimeoutException: armor not equipped")
            armor = None
        item_tier = charm.text.replace('+',"").split('\n')[-1]
        self.action.move_to_element(charm).perform()
        try:
            charm_stats_popup = WebDriverWait(self.driver, .5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'tbItemDesc'))
            )
            charm = Charm(charm_stats_popup, item_tier)
        except TimeoutException:
            self.logger.info(f"{self.name} --> TimeoutException: charm not equipped")
            charm = None
        item_tier = acc_charm.text.replace('+',"").split('\n')[-1]
        self.action.move_to_element(acc_charm).perform()
        try:
            charm_stats_popup = WebDriverWait(self.driver, .5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'tbItemDesc'))
            )
            acc_charm = Charm(charm_stats_popup, item_tier)
        except TimeoutException:
            self.logger.info(f"{self.name} --> TimeoutException: acc_charm not equipped")
            acc_charm = None
        return weapon, armor, charm, acc_charm
    def load_equipment(self):
        self.logger.info(f"{self.name} --> reading inventory equipment")
        equipment = {}
        self.action.send_keys(Keys.SPACE).perform()
        self.action.send_keys("i").perform()
        equipment_container = WebDriverWait(self.driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'invEqBox'))
        )
        equipment_elements = WebDriverWait(equipment_container, 1).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'itemSlotBox'))
        )
        # Enumerate the equipment slots to see if there is an item,
        #   and if so in which slot
        for index, element in enumerate(equipment_elements):
            self.logger.info(f"{self.name} --> reading inventory item {index} icon tier/bonus overlay")
            try:
                item_element = element.find_element(By.CLASS_NAME, 'itemBox')
                item_tier = item_element.text.replace('+',"").split('\n')[-1]
                self.action.move_to_element(item_element).perform()
                item_comparison_grouping = WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'tbItemDesc'))
                )
                item_description_element = item_comparison_grouping.find_elements(By.XPATH, "./child::*")[0]
                item = self.convert_item_from_element(item_description_element, item_tier)
                equipment[index] = item
            except NoSuchElementException:
                self.logger.info(f"{self.name} --> NoSuchElementException: No equipment in slot {index}")
                equipment[index] = None
                continue
        return equipment
    def classify_item(self, item_name:str) -> str:
        self.logger.info(f"{self.name} --> classifying {item_name=}")
        weapon_types = ["sword","club","axe","dagger","staff","longsword","warhammer","battleaxe","spear","polearm"]
        charm_types = ["ice","fire","lightning","wind","earth","wild Heal","heal","focused heal"]
        armor_types = ["robe","padded Robe","leather armor","scale armor","chain mail","plate mail"]
        for weapon_type in weapon_types:
            if weapon_type in item_name.lower():
                self.logger.info(f"{self.name} --> {item_name=} is weapon")
                return "weapon"
        for armor_type in armor_types:
            if armor_type in item_name.lower():
                self.logger.info(f"{self.name} --> {item_name=} is armor")
                return "armor"
        for charm_type in charm_types:
            if charm_type in item_name.lower():
                self.logger.info(f"{self.name} --> {item_name=} is charm")
                return "charm"         
    def convert_item_from_element(self, item_popup_element, item_tier):
        if isinstance(item_popup_element, str):
            item_name = item_popup_element.split('\n')[0]
        else:
            item_name = item_popup_element.text.split('\n')[0]
        self.logger.info(f"{self.name} --> parsing {item_name=} into item object")
        item_classification = self.classify_item(item_name)
        if item_classification == "weapon":
            item = Weapon(item_popup_element, item_tier)
            self.logger.info(f"{self.name} --> {item_name=} parsed to weapon item object")
        elif item_classification == "armor":
            item = Armor(item_popup_element, item_tier)
            self.logger.info(f"{self.name} --> {item_name=} parsed to armor item object")
        elif item_classification == "charm":
            item = Charm(item_popup_element, item_tier)
            self.logger.info(f"{self.name} --> {item_name=} parsed to charm item object")
        else:
            self.logger.error(f"{self.name} --> could not parse {item_name=} to item object")
            item = None
        return item        
    def delete_item(self, item_element):
        inventory_window_element = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'invIWSide'))
        )
        trash_bin_element = inventory_window_element.find_element(By.XPATH, '//*[@id="stage"]/div[5]/div[4]/div[3]/div')
        self.action.drag_and_drop(item_element, trash_bin_element).perform()
#-----------------------------------------------
class NavigationController:
    def __init__(self, driver, logger) -> None:
        self.name = "NavigationController"
        self.driver = driver
        self.logger = logger
        self.last_move = None
    def find_walls(self):
        self.logger.info(f"{self.name}.find_walls()")
        walls = {
            'left':False,
            'right':False,
            'front':False
        }
        try:
            # - get all rect elements in maze-bg-svg
            maze_svg = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'mazeSVG')))
            maze_svg_rects = WebDriverWait(maze_svg, 3).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'rect')))
            # - find the ones equal centered x,y coordinates (meaning they are centered)
            # - exclude any the positioned at 0,0 because that is the rect making up the maze_bg and not actually a wall
            centered_svg_rects = []
            maze_bg_svg_size = 0
            for rect_element in maze_svg_rects:
                if float(rect_element.get_attribute('x').replace('px', '').replace('-', '')) ==  float(rect_element.get_attribute('y').replace('px', '').replace('-', '')):
                    if float(rect_element.get_attribute('y').replace('px', '').replace('-', '')) == 0:
                        maze_bg_svg_size = int(rect_element.get_attribute('height').replace('px', '').replace('-', ''))
                    else:
                        centered_svg_rects.append(rect_element)
            if len(centered_svg_rects) != 0:
                # - get the largest of those centered wall rects
                closest_wall_svg = None
                for wall_svg_element in centered_svg_rects:
                    if closest_wall_svg == None:
                        closest_wall_svg = wall_svg_element
                    else:
                        if wall_svg_element.size['height'] > closest_wall_svg.size['height']:
                            closest_wall_svg = wall_svg_element
                # -- this rect will be the closest wall the player is facing
                # its size in comparison to the size of the maze_bg_svg indicates how close the player is to the wall
                # closest_wall_size_percent = int((closest_wall_svg.size['height']/maze_bg_svg_size['height'])*100)
                closest_wall_height = float(closest_wall_svg.get_attribute('height').replace('px', '').replace('-', ''))
                closest_wall_size_percent = int((closest_wall_height/maze_bg_svg_size)*100)
                if closest_wall_size_percent >= 66:
                    walls['front'] = True
        except:
            self.logger.info(f"{self.name}.find_walls() --> No svg rect elements found")
        # the maze_svg_paths are walls that are not drawn as rects and can be used to see if there is a wall to the left or right of the player
        try:
            maze_svg_paths = WebDriverWait(maze_svg, 3).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'path')))
            for path_element in maze_svg_paths[-5:]:
                if path_element.size['height'] > maze_svg.size['height'] and path_element.size['height'] != path_element.size['width']:
                    if path_element.location['x'] == 50 and path_element.location['y'] == -165:
                        walls['left'] = True
                    # if path_element.location['x'] == 250:
                    if path_element.location['x'] == 583 and path_element.location['y'] == -165:
                        walls['right'] = True
        except:
            self.logger.info(f"{self.name}.find_walls() No svg path elements found")
        self.logger.info(f"{self.name}.find_walls() --> {walls=}")
        return walls
    def nav(self):
        self.logger.info(f"{self.name}.nav()")
        # the 'left hand on wall' maze solution method
        # known flaw -> if on a wall section that does not connect to edge of maze, player will circle that wall section forever
        move = None
        walls = self.find_walls()
        walls = (walls['left'], walls['right'], walls['front'])
        self.logger.info(f"{self.name}.nav() --> {walls=}")
        if walls == (False, False, False):
            if self.last_move == 'right':
                move = 'forward'
            else:
                move = choice(['right','forward'])
        elif walls == (False, False, True):
            move = 'right'
        elif walls == (False, True, False):
            possible_moves = ['left', 'forward']
            if self.last_move in possible_moves:
                possible_moves.remove(self.last_move)
            move = choice(possible_moves)
            #------
            # if self.last_move == 'left':
            #     move = 'forward'
            # else:
            #     move = choice(['left','forward'])
        elif walls == (False, True, True):
            move = 'left'
        elif walls == (True, False, False):
            move = 'forward'
        elif walls == (True, False, True):
            move = 'right'
        elif walls == (True, True, False):
            move = 'forward'
        elif walls == (True, True, True):
            move = 'right'
        self.logger.info(f"{self.name}.nav() {move=}")
        self.last_move = move
        return move
#-----------------------------------------------
class VaultController:
    def __init__(self, driver, logger) -> None:
        self.name = "VaultController"
        self.logger = logger
        self.driver = driver
        self.action = ActionChains(self.driver)
        self.equipment = self.get_character_vault_equipment()
        self.level_to_tier_map = {
            0: "III (0)",
            5: "IV (5)",
            10: "V (10)",
            15: "VI (15)",
            20: "VII (20)",
            25: "VIII (25)",
            30: "IX (30)",
            35: "X (35)",
            40: "XI (40)",
            45: "XII (45)",
            50: "XIII (50)",
            55: "XIV (55)"
        } 
        self.tier_to_tier_map = {
            "III": "III (0)",
            "IV": "IV (5)",
            "V": "V (10)",
            "VI": "VI (15)",
            "VII": "VII (20)",
            "VIII": "VIII (25)",
            "IX": "IX (30)",
            "X": "X (35)",
            "XI": "XI (40)",
            "XII": "XII (45)",
            "XIII": "XIII (50)",
            "XIV": "XIV (55)"
        }  
        self.item_type_to_search_type_map = {
            'weapon' : 'Weapons',
            'armor' : 'Armor',
            'charm' : 'Charms',
            'acc_charm' : 'Charms'
        }
    def _open(self):
        self.action.send_keys(Keys.SPACE).perform()
        self.action.send_keys("v").perform()
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'vaultTabs'))
            )
        except TimeoutError as e:
            raise e
    def open_tab(self, tab_name):
        self.logger.info(f"{self.name}.open_tab({tab_name=})")
        self._open()
        market_tabs = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'vaultTabs'))
        )
        vault, withdraw, deposit, transfer = market_tabs.find_elements(By.CLASS_NAME, 'njRB')
        tab_elements = {
            'vault' : vault,
            'withdraw' : withdraw,
            'deposit' : deposit,
            'transfer' : transfer
        }
        # tab_elements[tab_name].click()
        self.driver.execute_script("arguments[0].click();", tab_elements[tab_name])
        return
    def _should_deposit(self, item_tier, item_stats):
        stats_per_tier = deposit_criteria.get(item_tier)
        if stats_per_tier == None:
            return False
        for stat in item_stats:
            if stat in stats_per_tier:
                return True
        return False
    def get_best_equipable(self, character_class, item_tier) -> dict:
        self.logger.info(f"{self.name}.get_best_equipable()")
        file_name = Path(str(importlib.resources.files("ladderbot")) + "\\vault_equipment.xlsx")
        self.logger.info(f"{self.name}.get_best_equipable() --> reading excel file {file_name=}, {character_class=}")
        items_dataframe = pd.read_excel(file_name, sheet_name=character_class, index_col=0)
        best_equipable = {
            'weapon' : items_dataframe.loc["weapon", item_tier],
            'armor' : items_dataframe.loc["armor", item_tier],
            'charm' : items_dataframe.loc["charm", item_tier],
            # 'acc_charm' : items_dataframe.loc["acc_charms", item_tier]
        }
        for item_type in best_equipable:
            try:
                best_equipable[item_type] = best_equipable[item_type].split('\n')[0]
            except:
                best_equipable[item_type] = None
        self.logger.info(f"{self.name}.get_best_equipable() --> {best_equipable=}")
        return best_equipable
    def get_character_vault_equipment(self) -> tuple:
        file_name = Path(str(importlib.resources.files("ladderbot")) + "\\vault_equipment.xlsx")
        items_dataframe = pd.read_excel(file_name, sheet_name=self.get_player_class(), index_col=0)
        # List of usable weapon objects from spreadsheet
        res = [(items_dataframe.loc["weapon", tier], tier) for tier in items_dataframe.columns]
        weapons = [Weapon(item_data[0], item_data[1]) for item_data in res if isinstance(item_data[0], str)]
        # List of usable armor objects from spreadsheet
        res = [(items_dataframe.loc["armor", tier], tier) for tier in items_dataframe.columns]
        armor = [Armor(item_data[0], item_data[1]) for item_data in res if isinstance(item_data[0], str)]
        # List of usable charm objects from spreadsheet
        res = [(items_dataframe.loc["charm", tier], tier) for tier in items_dataframe.columns]
        charms = [Charm(item_data[0], item_data[1]) for item_data in res if isinstance(item_data[0], str)]
        return (*weapons, *armor, *charms)
    def search(self, item_type, tier_min, tier_max, item_name):
        self.logger.info(f"{self.name}.search({item_type, tier_min, tier_max, item_name})")
        vault_controls = self.driver.find_element(By.CLASS_NAME, 'vltControls')
        selection_fields = vault_controls.find_elements(By.TAG_NAME, 'select')
        type_select = Select(selection_fields[1])
        min_level_select = Select(selection_fields[3])
        max_level_select = Select(selection_fields[4])
        search_button = WebDriverWait(vault_controls, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'abutGradBl'))
        )
        min_level_select.select_by_visible_text(self.tier_to_tier_map[tier_min])
        max_level_select.select_by_visible_text(self.tier_to_tier_map[tier_max])
        type_select.select_by_visible_text(self.item_type_to_search_type_map[item_type])
        # search the vault for results
        self.driver.execute_script("arguments[0].click();", search_button)
        try:
            search_results_box = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'vltItemsBox'))
            )
        except:
            return None
        try:
            search_result_item_elements = WebDriverWait(search_results_box, 5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'itemBox'))
            )
        except:
            return None
        # for every found item for that tier/type in the vault
        for index, element in enumerate(search_result_item_elements):
            self.logger.info(f"{self.name} --> reading vault search result {index} icon tier/bonus overlay")
            # get the items details
            self.action.move_to_element(element).perform()
            item_comparison_grouping = WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'tbItemDesc'))
            )
            item_popup_element = item_comparison_grouping.find_elements(By.XPATH, "./child::*")[0]
            item_tier = element.text.replace('+',"").split('\n')[-1]
            found_item = self.convert_item_from_element(item_popup_element, item_tier)
            # compare it to the item name we're looking for
            if found_item.name.lower() == item_name.lower():
                return element
        else:
            return None
    def _withdraw(self, item_element):
        self.logger.info(f"{self.name}._withdraw({item_element=})")
        if item_element is not None:
            ActionChains(self.driver) \
            .key_down(Keys.CONTROL) \
            .click(item_element) \
            .key_up(Keys.CONTROL) \
            .perform()
    def _equip(self, item_element):
        self.logger.info(f"{self.name}._equip({item_element=})")
        if item_element is not None:
            ActionChains(self.driver) \
            .key_down(Keys.CONTROL) \
            .click(item_element) \
            .key_up(Keys.CONTROL) \
            .perform()
    def get_player_level(self):
        self.logger.info(f"{self.name}.get_player_level()")
        self.action.send_keys(Keys.SPACE).perform()
        self.action.send_keys("c").perform()
        level_container = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, 'CS0'))
        )
        player_level = int(level_container.text)
        self.action.send_keys(Keys.SPACE).perform()
        self.logger.info(f"{self.name}.get_player_level() --> {player_level=}")
        return player_level
    def get_player_class(self):
        self.logger.info(f"{self.name}.get_player_class()")
        self.action.send_keys(Keys.SPACE).perform()
        self.action.send_keys("c").perform()
        stats_container = WebDriverWait(self.driver, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'fsLegend')))[0]
        player_class_element = WebDriverWait(stats_container, 3).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'div')))[2]
        player_class = player_class_element.text
        self.action.send_keys(Keys.SPACE).perform()
        self.logger.info(f"{self.name}.get_player_class() --> {player_class=}")
        return player_class
    def equip_best(self):
        self.logger.info(f"{self.name}.equip_best()")
        # round down player level to nearest multiple of 5
        player_class = self.get_player_class()
        player_level = 5 * math.floor(self.get_player_level() / 5)
        if player_level > 55: player_level = 55
        # use that number to get the necessary item tier from self.level_to_tier_map
        tier = self.level_to_tier_map[player_level].split(' ')[0]
        # look up the best item for the character class using that tier
        best_equipable = self.get_best_equipable(player_class, tier)
        # for the items we wish to find in the vault
        for item in best_equipable:
            if best_equipable[item] is None:
                continue
            # set the item search type to either weapon,armor,charm
            if item == 'acc_charms':
                item_type = 'Charms'
            else:
                item_type = item
            item_name = best_equipable[item]
            # search vault for the item
            # open the vault to the withdraw tab
            self.open_tab('withdraw')
            vault_item_element = self.search(item_type, tier, tier, item_name)
            # if the item is found withdraw it
            if vault_item_element is not None:
                self._withdraw(vault_item_element)
                # search inventory equipment for the withdrawn item
                item_element_to_equip = self.find_inventory_equipment_element(item_name)
                # if it is found
                if item_element_to_equip is not None:
                    # equip it
                    self._equip(item_element_to_equip)
        # close the menus
        self.action.send_keys(Keys.SPACE).perform()
    def find_inventory_equipment_element(self, item_name):
        self.logger.info(f"{self.name}.find_inventory_equipment_element({item_name=})")
        WebDriverWait(self.driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'invTabs'))
        ).click()
        equipment_container = WebDriverWait(self.driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'invEqBox'))
        )
        equipment_elements = WebDriverWait(equipment_container, 1).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'itemSlotBox'))
        )
        # Enumerate the equipment slots to see if there is an item,
        #   and if so in which slot
        for element in equipment_elements:
            try:
                item_element = element.find_element(By.CLASS_NAME, 'itemBox')
            except NoSuchElementException:
                # Item equipment slot was empty
                continue
            self.action.move_to_element(item_element).perform()
            item_comparison_grouping = WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'tbItemDesc'))
            )
            item_popup_element = item_comparison_grouping.find_elements(By.XPATH, "./child::*")[0]
            inventory_item_name = item_popup_element.text.split("\n")[0]
            if item_name.lower() == inventory_item_name.lower():
                self.logger.info(f"{self.name}.find_inventory_equipment_element({item_name=}) --> equipment element found")
                return element
        else:
            self.logger.info(f"{self.name}.find_inventory_equipment_element({item_name=}) --> equipment element not found")
            return None
    def deposit_item(self, item_name):
        self.logger.info(f"{self.name}.deposit_item({item_name=})")
        self.open_tab("deposit")
        inventory_element = self.find_inventory_equipment_element(item_name)
        if inventory_element is not None:
            # if they have the same name, deposit the item from the vault
            ActionChains(self.driver) \
            .key_down(Keys.LEFT_SHIFT) \
            .click(inventory_element) \
            .key_up(Keys.LEFT_SHIFT) \
            .perform()
            vault_deposit_button = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'vDepB'))
            )
            # will click deposit button even if behind another element
            # vault_deposit_button.click()
            self.driver.execute_script("arguments[0].click();", vault_deposit_button)
            return True
        else:
            return False
    def classify_item(self, item_name:str) -> str:
        self.logger.info(f"{self.name} --> classifying {item_name=}")
        weapon_types = ["sword","club","axe","dagger","staff","longsword","warhammer","battleaxe","spear","polearm"]
        charm_types = ["ice","fire","lightning","wind","earth","wild Heal","heal","focused heal"]
        armor_types = ["robe","padded Robe","leather armor","scale armor","chain mail","plate mail"]
        for weapon_type in weapon_types:
            if weapon_type in item_name.lower():
                self.logger.info(f"{self.name} --> {item_name=} is weapon")
                return "weapon"
        for armor_type in armor_types:
            if armor_type in item_name.lower():
                self.logger.info(f"{self.name} --> {item_name=} is armor")
                return "armor"
        for charm_type in charm_types:
            if charm_type in item_name.lower():
                self.logger.info(f"{self.name} --> {item_name=} is charm")
                return "charm"         
    def convert_item_from_element(self, item_popup_element, item_tier):
        if isinstance(item_popup_element, str):
            item_name = item_popup_element.split('\n')[0]
        else:
            item_name = item_popup_element.text.split('\n')[0]
        self.logger.info(f"{self.name} --> parsing {item_name=} into item object")
        item_classification = self.classify_item(item_name)
        if item_classification == "weapon":
            item = Weapon(item_popup_element, item_tier)
            self.logger.info(f"{self.name} --> {item_name=} parsed to weapon item object")
        elif item_classification == "armor":
            item = Armor(item_popup_element, item_tier)
            self.logger.info(f"{self.name} --> {item_name=} parsed to armor item object")
        elif item_classification == "charm":
            item = Charm(item_popup_element, item_tier)
            self.logger.info(f"{self.name} --> {item_name=} parsed to charm item object")
        else:
            self.logger.error(f"{self.name} --> could not parse {item_name=} to item object")
            item = None
        return item 
#-----------------------------------------------
class MarketController:
    def __init__(self, driver, logger, gold_password) -> None:
        self.name = "MarketController"
        self.logger = logger
        self.gold_password = gold_password
        self.driver = driver
        self.action = ActionChains(self.driver)  
    def open(self):
        self.action.send_keys(Keys.SPACE).perform()
        self.action.send_keys("m").perform()
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'marketTabs'))
            )
        except TimeoutError as e:
            raise e
    def _open_sell_tab(self):
        self.open()
        market_tabs = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'marketTabs'))
        )
        search, sell, transfer = market_tabs.find_elements(By.CLASS_NAME, 'njRB')
        # sell.click()
        self.driver.execute_script("arguments[0].click();", sell)
        return
    def search(self, type:str=None, subtype:str=None, min_level:int=None, max_level:int=None, min_magic:int=None, max_magic:int=None, min_cost:int=0, max_cost:int=999999, attribute1:str=None, attribute2:str=None, attribute3:str=None, only_equipable:bool=False):
        market_controls = self.driver.find_element(By.CLASS_NAME, 'marketControls')
        selection_fields = Select(market_controls.find_elements(By.TAG_NAME, 'select'))
        if type:
            type_select = selection_fields[0]
            type_select.select_by_visible_text(type)
        if subtype:
            subtype_select = selection_fields[1]
            subtype_select.select_by_visible_text(subtype)
        level_map = {
                1: "I (0)",
                2: "II (0)",
                3: "III (0)",
                5: "IV (5)",
                10: "V (10)",
                15: "VI (15)",
                20: "VII (20)",
                25: "VIII (25)",
                30: "IX (30)",
                35: "X (35)",
                40: "XI (40)",
                45: "XII (45)",
                50: "XIII (50)",
                55: "XIV (55)"
            }        
        if min_level:
            min_level_select = selection_fields[2]
            min_level_select.select_by_visible_text(level_map[min_level])
        if max_level:
            max_level_select = selection_fields[3]
            max_level_select.select_by_visible_text(level_map[max_level])
        if min_magic:
            min_magic_select = selection_fields[4]
            min_magic_select.select_by_visible_text(level_map[min_magic])
        if max_magic:
            max_magic_select = selection_fields[5]
            max_magic_select.select_by_visible_text(level_map[max_magic])
        if min_cost:
            self.driver.find_element(By.XPATH, '//*[@id="stage"]/div[5]/div[2]/div[1]/div[5]/input[1]').send_keys(str(min_cost))
        if max_cost and max_cost != 999999:
            self.driver.find_element(By.XPATH, '//*[@id="stage"]/div[5]/div[2]/div[1]/div[5]/input[2]').send_keys(str(max_cost))
        if attribute1:
            attribute1 = {
                'Enhanced Effect' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[2]',
                'Strength' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[3]',
                'Dexterity' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[4]',
                'Vitality' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[5]',
                'Intelligence' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[6]',
                'Max Life' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[7]',
                'Max Mana' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[2]',
                'Experience Gained' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[8]',
                'Magic Luck' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[9]',
                'Life Regen' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[10]',
                'Mana Regen' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[11]',
                'Extra Equipment Slots' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[12]',
                'Critical Strike' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[13]',
                'Life per Attack' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[14]',
                'Mana per Attack' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[15]',
                'Life per Kill' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[16]',
                'Mana per Kill' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[17]',
                'Life Steal' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[18]',
                'Damage Return' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[19]',
                'Mind Numb' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[20]',
                'Armor Pierce' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[22]',
                'Parry' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[22]',
                'Critical Flux' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[22]',
                'Physical Damage Reduction' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[24]',
                'Magical Damage Reduction' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[25]',
                'Mana Syphon' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[26]',
                'Quick Draw' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[27]',
                'Mana Consumption' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[28]',
                'Heal Mastery' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[29]',
                'Mana Skin' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[30]',
                'Power Shot' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[31]',
                'Glancing Blow' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[32]',
                'Jubilance' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[33]',
                'Ice Mastery' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[34]',
                'Fire Mastery' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[35]',
                'Lightning Mastery' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[36]',
                'Wind Mastery' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[37]',
                'Earth Mastery' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[38]',
                'Quantity' : '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/select/option[39]'
            }
            self.driver.find_element(By.XPATH, '//*[@id="stage"]/div[5]/div[2]/div[1]/div[6]/input').send_keys(str(1))
            self.driver.find_element(By.XPATH, attribute1['Vitality']).click()
        if attribute2:
            attribute2 = {k:v.replace('div[6]','div[7]') for k,v in attribute1.items()}
            self.driver.find_element(By.XPATH, '//*[@id="stage"]/div[5]/div[2]/div[1]/div[7]/input').send_keys(str(1))
            self.driver.find_element(By.XPATH, attribute2['Vitality']).click()
        if attribute3:
            attribute3 = {k:v.replace('div[6]','div[8]') for k,v in attribute1.items()}
            self.driver.find_element(By.XPATH, '//*[@id="stage"]/div[5]/div[2]/div[1]/div[8]/input').send_keys(str(1))
            self.driver.find_element(By.XPATH, attribute3['Vitality']).click()
    def sell_equipment(self, player_equipment):
        for item_index in player_equipment:
            if player_equipment[item_index] is None:
                self.logger.info(f"{self.name} --> No equipment in slot {item_index}")
                continue
            rarity = player_equipment[item_index].rarity
            tier = player_equipment[item_index].tier
            price = self._should_sell(rarity, tier)
            if price is not None:
                self._sell(item_index, price)
        self.action.send_keys(Keys.SPACE).perform()
    def _sell(self, equipment_item_index, price):
        self.action.send_keys(Keys.SPACE).perform()
        self.action.send_keys("m").perform()
        self._open_sell_tab()
        equipment_container = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'invEqBox'))
        )
        equipment_elements = WebDriverWait(equipment_container, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'itemSlotBox'))
        )
        equipment_element_to_sell = equipment_elements[equipment_item_index]
        ActionChains(self.driver) \
        .key_down(Keys.SHIFT) \
        .click(equipment_element_to_sell) \
        .key_up(Keys.SHIFT) \
        .perform()
        cost_field = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, 'mkSellCost'))
        )
        cost_field.clear()
        cost_field.send_keys(f"{price}")  # Replace YOUR_USERNAME with your actual username
        gold_pw_field = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, 'mkGpwd'))
        )
        gold_pw_field.clear()
        gold_pw_field.send_keys(self.gold_password)
        sell_item_button = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, 'mkBuySell'))
        )
        # sell_item_button.click()
        self.driver.execute_script("arguments[0].click();", sell_item_button)
        sleep(1)
    def _should_sell(self, item_rarity, item_tier):
        prices_per_level = prices.get(item_rarity)
        if prices_per_level == None:
            return False
        price = prices_per_level.get(item_tier)
        return price
#-----------------------------------------------
class TransmuteController:
    def __init__(self, driver, logger) -> None:
        self.name = "TransmuteController"
        self.logger = logger
        self.driver = driver
        self.action = ActionChains(self.driver)
        self.blacklist = []
    def transmute_equipment(self, player_transmute_rank, player_equipment):
        self.logger.info(f"{self.name}.transmute_equipment --> Starting transmute routine")
        self.logger.info(f"{self.name}.transmute_equipment({player_equipment=})")
        self.action.send_keys(Keys.SPACE).perform()
        performed_transmute = False
        if player_equipment is not None:
            for item_index in player_equipment:
                item = player_equipment[item_index]
                if item and self._should_transmute(item, player_transmute_rank):
                    self._transmute(item_index)
                    performed_transmute = True
        return performed_transmute
    def _should_transmute(self, item, player_transmute_rank):
        self.logger.info(f"{self.name} --> checking if {item} should be transmuted")
        if item in self.blacklist:
            self.logger.info(f"{self.name}_should_transmute --> {item} in blacklist. skipping")
            return False
        tier_mapping = transmute_mapping.get(item.tier)
        if item.rarity in tier_mapping['rarity_levels']:
            if tier_mapping["ranks"]["min"] <= player_transmute_rank <= tier_mapping["ranks"]["max"]:
                return True
        return False
    def _transmute(self, equipment_item_index):
        self.logger.info(f"{self.name} --> transmuting item {equipment_item_index}")
        self.action.send_keys(Keys.SPACE).perform()
        # open transmute menu
        transmute_town_element = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, 'townObj6'))
        )
        # transmute_town_element.click()
        self.driver.execute_script("arguments[0].click();", transmute_town_element)
        # get equipment container
        equipment_container = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'invEqBox'))
        )
        # get equipment elements[]
        equipment_elements = WebDriverWait(equipment_container, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'itemSlotBox'))
        )
        element_to_transmute = equipment_elements[equipment_item_index]
        ActionChains(self.driver) \
        .key_down(Keys.SHIFT) \
        .click(element_to_transmute) \
        .key_up(Keys.SHIFT) \
        .perform()
        begin_transmute_button = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'skBut'))
        )
        # begin_transmute_button.click()
        self.driver.execute_script("arguments[0].click();", begin_transmute_button)
        sleep(.25)
        # container that appears after starting the transmute skill 'mini-game'
        transmute_skill_container = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'skillBody'))
        )
        try:
            # buttons from within the transmute mini-game container
            transmute_skill_element_buttons = WebDriverWait(self.driver, 3).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'skBut'))
            )
            transmute_button = transmute_skill_element_buttons[0]
            stabilize_button = transmute_skill_element_buttons[1]
        except IndexError:
            self.logger.debug(f"{self.name} IndexError --> transmute or stabilize button not found")
            return
        if transmute_button.text.strip() == "Stabilize":
            transmute_button, stabilize_button = stabilize_button, transmute_button
        self.logger.info(f"{self.name} --> starting transmutation minigame")
        while True:
            try:
                volatality_progress_meter, transmute_progress_meter = WebDriverWait(transmute_skill_container, 3).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'meterBoxProg'))
                )
            except TimeoutException:
                self.logger.debug(f"{self.name} --> TimeoutException: couldn't locate volatility or transmutation progress meter")
                break
            except StaleElementReferenceException:
                self.logger.debug(f"{self.name} --> StaleElementReferenceException: volatility or transmutation progress meter became stale")
                break
                # transmute_progress_value = 100 - int(transmute_progress_meter.value_of_css_property('width').replace("%", ''))
            volatality_progress_value = int(volatality_progress_meter.get_attribute("style").split(";")[2].replace(' ', '').replace('%', '').split(":")[1])
            if volatality_progress_value >= 50:
                try:
                    # stabilize_button.click()
                    self.driver.execute_script("arguments[0].click();", stabilize_button)
                except:
                    self.logger.info(f"{self.name} --> TimeoutException: couldn't click stabilize button")
                    break
            else:
                try:
                    # transmute_button.click()
                    self.driver.execute_script("arguments[0].click();", transmute_button)
                except StaleElementReferenceException as e:
                    self.logger.info(f"{self.name} --> TimeoutException: couldn't click transmute button")
                    break
                # elements will change if the transmute is complete or volatility completes
                # this will raise an exception indicating and indicates the action is complete
                # return
        self.action.send_keys(Keys.SPACE).perform()
        self.logger.info(f"{self.name} --> done transmuting item {equipment_item_index}")
        return
#-----------------------------------------------
class TransferController:
    def __init__(self, driver, logger) -> None:
        self.name = "TransferController"
        self.driver = driver
        self.logger = logger
        self.action = ActionChains(self.driver)
        self.blacklist = []
    def _should_transfer(self, item):
        self.logger.info(f"{self.name}._should_transfer({item=})")
        if item in self.blacklist:
            self.logger.info(f"{self.name}_should_transfer --> {item} in blacklist. skipping")
            return False
        if set(item.stats).intersection(desireable_stats_mapping[item.tier]):
            return True
        return False
    def transfer_items(self, player_equipment):
        self.logger.info(f"{self.name}.transfer_items({player_equipment=})")
        self.open_transfer_tab()
        performed_transfer = False
        if player_equipment is not None:
            for item_index in player_equipment:
                item = player_equipment[item_index]
                if item and self._should_transfer(item):
                    performed_transfer = self._transfer(item_index)
        self.action.send_keys(Keys.SPACE).perform()
        return performed_transfer
    def _transfer(self, equipment_item_index):
        self.logger.info(f"{self.name}._transfer({equipment_item_index=})")
        character_elements = WebDriverWait(self.driver, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'marketChars')))
        self.logger.info(f"{self.name}._transfer {character_elements=}")
        # get equipment container
        equipment_container = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'invEqBox')))
        self.logger.info(f"{self.name}._transfer {equipment_container=}")
        # get equipment elements[]
        equipment_elements = WebDriverWait(equipment_container, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'itemSlotBox')))
        self.logger.info(f"{self.name}._transfer {equipment_elements=}")
        inventory_item_element = equipment_elements[equipment_item_index]
        inventory_tab_element = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'invTabs'))
        )
        self.logger.info(f"{self.name}._transfer {inventory_tab_element=}")
        self.driver.execute_script("arguments[0].click();", inventory_tab_element)
        # inventory_tab_element.click()
        ActionChains(self.driver) \
            .key_down(Keys.LEFT_SHIFT) \
            .click(inventory_item_element) \
            .key_up(Keys.LEFT_SHIFT) \
            .perform()
        for character_element in character_elements:
            market_tabs_element = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'marketTabs')))
            self.driver.execute_script("arguments[0].click();", market_tabs_element)
            character_element.click()
            transfer_button = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'mkBuySell')))
            item_transfer_Box = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'mkXfer')))
            WebDriverWait(item_transfer_Box, 1).until(EC.presence_of_element_located((By.CLASS_NAME, 'itemBox')))
            
            # self.driver.execute_script("arguments[0].click();", transfer_button)
            attempts = 0
            while attempts <= 4:
                self.logger.info(f"{self.name}._transfer --> {attempts=}")
                transfer_button.click()
                sleep(1)
                try:
                    # if the item it still in the transfer box then the character it attemted to transfer to is likely full
                    WebDriverWait(item_transfer_Box, 1).until(EC.presence_of_element_located((By.CLASS_NAME, 'itemBox')))
                    self.logger.info(f"{self.name}._transfer --> Item transfer failed")
                    # so try the next character in the list
                    continue
                except:
                    self.logger.info(f"{self.name}._transfer --> Item transfer success")
                    # exception is raised if the item is no longer in the item transfer box which means it was transferred successfully
                    return True
    def _open(self):
        self.logger.info(f"{self.name}._open --> Opening menu")
        self.action.send_keys(Keys.SPACE).perform()
        self.action.send_keys("m").perform()
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'marketTabs')))
    def open_transfer_tab(self):
        self.logger.info(f"{self.name}.open_transfer_tab()")
        self._open()
        market_tabs = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'marketTabs')))
        search, sell, transfer = WebDriverWait(market_tabs, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'njRB')))
        self.driver.execute_script("arguments[0].click();", transfer)
        return
#-----------------------------------------------
class LevelingController:
    def __init__(self, driver, logger) -> None:
        self.name = "LevelingController"
        self.logger = logger
        self.driver = driver
        self.action = ActionChains(self.driver)
        self.character_class = None
        self.stat_element_map = {
            'level' : 'CS0',
            'strength' : 'CS3',
            'dexterity' : 'CS4',
            'intelligence' : 'CS5',
            'vitality' : 'CS6',
            'stat_points' : 'CS7',
            'ability_points' : 'CS8'
        }
        self.weapon_ability_map = {
            'powerstrike': 0,
            'retribution': 4
        }
        self.cast_ability_map = {
            'powercast': 2
        }
    def run(self):
        self.logger.info(f"{self.name} --> Performing leveling routine")
        self.character_class = self.get_character_class()
        stat_point_used = False
        if self.character_class in ['warlock', 'alchemist']:
            while self.stat_points_available():
                if self._get_ability_level('vitality') < 85:
                    self.use_stat_point('vitality')
                else:
                    self.use_stat_point('intelligence')
                stat_point_used = True
            while self.ability_points_available():
                self.use_ability_point('cast', 'powercast')
        else:
            while self.stat_points_available():
                self.use_stat_point("vitality")
                stat_point_used = True
            while self.ability_points_available():
                powerstrike_ability_level = self._get_ability_level('weapon', 'powerstrike')
                retribution_ability_level = self._get_ability_level('weapon', 'retribution')
                if powerstrike_ability_level <= retribution_ability_level:
                    self.use_ability_point('weapon', 'powerstrike')
                else:
                    self.use_ability_point('weapon', 'retribution')
        return stat_point_used
    def get_character_class(self):
        self.logger.info(f"{self.name}.get_character_class() --> Checking character class type")
        self.action.send_keys(Keys.SPACE).perform()
        self.action.send_keys("c").perform()
        character_class_element = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="stage"]/div[5]/div/div[2]/fieldset[1]/div[1]/div[2]'))
        )
        character_class = character_class_element.text
        self.action.send_keys(Keys.SPACE).perform()
        return character_class.lower()
    def stat_points_available(self):
        self.logger.info(f"{self.name}.stat_points_available()")
        available_points = self._get_stat_level('stat_points')
        self.logger.info(f"{self.name}.stat_points_available() --> {available_points=}")
        if available_points > 0:
            return True
        else:
            return False
    def _get_stat_level(self, stat_name):
        self.logger.info(f"{self.name}._get_stat_level({stat_name=})")
        self.action.send_keys(Keys.SPACE).perform()
        self.action.send_keys("c").perform()
        element_id = self.stat_element_map[stat_name]
        stat_element = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        stat_level = stat_element.text
        self.action.send_keys(Keys.SPACE).perform()
        return int(stat_level)
    def use_stat_point(self, stat_name:str):
        self.logger.info(f"{self.name} --> Using stat point on {stat_name}")
        self.action.send_keys(Keys.SPACE).perform()
        self.action.send_keys("c").perform()
        # get vitality container
        element_id = self.stat_element_map[stat_name]
        stat_element = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        try:
            increase_stat_button = WebDriverWait(stat_element, 3).until(
                EC.presence_of_element_located((By.TAG_NAME, 'svg'))
            )
            increase_stat_button.click()
        except TimeoutException:
            self.logger.info(f"{self.name} --> Could not locate increase_stat_button")
        self.action.send_keys(Keys.SPACE).perform()
    def ability_points_available(self):
        self.logger.info(f"{self.name} --> Checking for available ability points")
        available_points = self._get_stat_level('ability_points')
        self.logger.info(f"{self.name}.ability_points_available --> {available_points}")
        if available_points > 0:
            return True
        else:
            return False
    def _get_ability_level(self, ability_type, ability_name):
        self.logger.info(f"{self.name}._get_ability_level({ability_name=})")
        ability_element = self._get_ability_element(ability_type, ability_name)
        ability_level = ability_element.text
        if not ability_level:
            self.logger.info(f"{self.name}._get_ability_level() --> setting ability_level to 0")
            ability_level = 0
        self.action.send_keys(Keys.SPACE).perform()
        return int(ability_level)
    def use_ability_point(self, ability_type, ability_name):
        self.logger.info(f"{self.name}.use_ability_point({ability_name=})")
        ability_element = self._get_ability_element(ability_type, ability_name)
        ability_element.click()
        self.action.send_keys(Keys.SPACE).perform()
    def _get_ability_element(self, ability_type, ability_name):
        self.logger.info(f"{self.name}._get_ability_element({ability_type=}, {ability_name=})")
        self.action.send_keys(Keys.SPACE).perform()
        self.action.send_keys("c").perform()
        if ability_type == 'weapon':
            element_id = 'sWAbs'
            ability_map = self.weapon_ability_map
        else:
            element_id = 'sCAbs'
            ability_map = self.cast_ability_map
        abilities_container = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        ability_elements = WebDriverWait(abilities_container, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'abilityIcon'))
        )
        ability_element = ability_elements[ability_map[ability_name]]
        return ability_element
#-----------------------------------------------   
class GroupHandler:
    def __init__(self, driver, logger) -> None:
        self.name = "GroupHandler"
        self.logger = logger
        self.driver = driver
    def create(self):
        command = "njs.sendBytes(60, 3, 2, 5)"
        self.driver.execute_script(command)
    def leave(self):
        command = "njs.sendBytes(60, 5)"
        self.driver.execute_script(command)
#-----------------------------------------------
class PlayerController:
    def __init__(self, driver, logger) -> None:
        self.name = "PlayerController"
        self.driver = driver
        self.logger = logger
        self.action = ActionChains(self.driver)
        self.location_map = {
            'marketplace':0,
            'catacombs':1,
            'shrine':2,
            'vault':3,
            'pond':4,
            'cooking':5,
            'transmuting':6,
            'glyphing':7,
            'suffusencing':8,
            'master_quest':9
        }
        self.rarities = ["plain","magical","rare","mystical","angelic","mythical","arcane","legendary","godly","epic","relic","artifact","unique"]
        self.transmute_rank = 0
    def check_health(self):
        self.logger.info(f"{self.name}.check_health() --> Checking player health")
        # health_element = self.driver.find_element(By.CLASS_NAME, 'lifeMeter')
        health_element = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'lifeMeter'))
        )
        current_health, max_health = health_element.text.replace(' ', '').split('/')
        self.logger.info(f"{self.name}.check_health() --> {current_health=}, {max_health=}")
        return {
            'current' : int(current_health),
            'max_health' : int(max_health),
            'percent' : int(100*(int(current_health)/int(max_health)))
        }
    def check_location(self) -> bool:
        indicators = {
            'town' : (By.CLASS_NAME, 'townOIcon'),
            'catacombs' : (By.CLASS_NAME, 'bgCata'),
            'pond' : (By.CLASS_NAME, 'fishDock'),
            'master_quest' : (By.CLASS_NAME, 'mqDoor'),
            'character_creation' : (By.CLASS_NAME, 'createCharWrap'),
            'character_selected' : (By.CLASS_NAME, 'clCharWrap'),
            'character_selection' : (By.XPATH, '//*[@id="bg"]/div[1]/a'),
        }
        for location in indicators:
            try:
                self.driver.find_element(*(indicators.get(location)))
                self.logger.info(f"{self.name}.check_location() --> at {location}")
                return location
            except Exception as e:
                # If an exception occured check the next location indicator
                self.logger.info(f"{self.name}.check_location() --> not at {location}")
                pass
        else:
            return False
    def go(self, location:str):
        # only expected to be used while player is at the Town
        self.logger.info(f"{self.name}.go() --> traveling {location=}")
        while True:
            self.close_all()
            location_button = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, f'townObj{self.location_map[location]}'))
            )
            # location_button.click()
            self.driver.execute_script("arguments[0].click();", location_button)
            sleep(.2)
            current_location = self.check_location()
            if current_location.lower() != location.lower():
                self.logger.info(f"{self.name}.go() --> error traveling {location=}")
                sleep(randint(5,12))
            else:
                return location
    def check_mana(self):
        mana_element = self.driver.find_element(By.CLASS_NAME, 'manaMeter')
        current_mana, max_mana = mana_element.text.replace(' ', '').split('/')
        return {
            'current' : int(current_mana),
            'max_mana' : int(max_mana),
            'percent' : int(100*(int(current_mana)/int(max_mana)))
        }
    def close_all(self):
        ActionChains(self.driver)\
        .send_keys(Keys.SPACE)\
        .perform()
    def move(self, direction:str):
        if direction == 'forward':
            ActionChains(self.driver)\
            .send_keys(Keys.UP)\
            .perform()
            return
        elif direction == 'backward':
            ActionChains(self.driver)\
            .send_keys(Keys.DOWN)\
            .perform()
            return
        elif direction == 'left':
            ActionChains(self.driver)\
            .send_keys(Keys.LEFT)\
            .perform()
            return
        elif direction == 'right':
            ActionChains(self.driver)\
            .send_keys(Keys.RIGHT)\
            .perform()
            return
        elif direction == 'whistle':
            ActionChains(self.driver)\
            .send_keys('g')\
            .perform()
    def exit_catacombs(self):
        # Spams exiting the catacombs until we've left
        while self.check_location() == 'catacombs':
            try:
                to_town_button =self.driver.find_element(By.CLASS_NAME, "gradRed")
                # to_town_button.click()
                self.driver.execute_script("arguments[0].click();", to_town_button)
            except Exception as e:
                # Failed to leave catacombs, keep trying forever. or die...
                pass
    def mobs_on_screen(self):
        mobs =  self.driver.find_elements(By.CLASS_NAME, "mob")
        return mobs
    def use_abilities(self):
        try:
            ability_elements = WebDriverWait(self.driver, 1).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'bbAbility'))
            )
        except:
            return
        try:
            ability_elements.reverse()
            for element in ability_elements:
                if 'gradRed' in element.get_attribute('class').split():
                    return
                if int(element.text.split()[0].replace('%', '')) >= 50:
                    element.click()
                    # self.driver.execute_script("arguments[0].click();", element)
                    return
        except StaleElementReferenceException as e:
            # an ability was used and disappeared unexpectedly
            return
        except TypeError as e:
            # no ability elements were found
            return
    def attack_mob(self):
        ActionChains(self.driver)\
            .send_keys('q')\
            .perform()
        try:
            mob = self.driver.find_elements(By.CLASS_NAME, "mob")[0]
            mob.click()
            # self.driver.execute_script("arguments[0].click();", mob)
        except Exception as e:
            self.move("whistle")      
    def check_for_drops(self):
        drop_elements = None
        try:
            drops_container = self.driver.find_element(By.CLASS_NAME, "dropItemsBox")
            drop_elements = drops_container.find_elements(By.CLASS_NAME, "itemBox")
        except:
            # if finding this container errors out, there's no drops
            pass
        return drop_elements
    def _should_pickup_drop(self, item_overlay_stats):
        tier_mapping = item_pickup_mapping.get(item_overlay_stats[1])
        if item_overlay_stats is None or tier_mapping is None:
            return False
        if self.rarities[int(item_overlay_stats[0])] in tier_mapping['rarity_levels']:
            if tier_mapping["ranks"]["min"] <= self.transmute_rank <= tier_mapping["ranks"]["max"]:
                return True
        return False
#-----------------------------------------------
class Player:
    def __init__(self, logger, player_controller:PlayerController, leveler:LevelingController, inventory:InventoryController, navigator:NavigationController, vault:VaultController, transmuter:TransmuteController, transfer_controller:TransferController) -> None:
        self.name = "Player"
        self.logger = logger
        self.controller: PlayerController = player_controller
        self.health: dict = self.controller.check_health()
        self.mana: dict = self.controller.check_mana()
        self.location: str = self.controller.check_location()
        self.transmute_rank: int = 0
        self.leveler: LevelingController = leveler
        self.inventory: InventoryController = inventory
        self.navigator: NavigationController = navigator
        self.vault: VaultController = vault
        self.transmuter: TransmuteController = transmuter
        self.transfer_controller: TransferController = transfer_controller
        if self.location == "catacombs":
            self.exit_catacombs()
    def run(self):
        self.transmuter.blacklist = self.vault.equipment
        self.transfer_controller.blacklist = self.vault.equipment
        self.inventory.load()
        pdb.set_trace()
        if len(self.inventory.equipment):
            self.transmute_items()
        if len(self.inventory.equipment):
            self.transfer_equipment()
        self.equip_best_gear()
        while True:
            self.update_health()
            # if the player explored the catacombs
            if not self.explore(enter_health_percent=100, exit_health_percent=30):
                continue
            if len(self.inventory.equipment):
                self.transmute_items()
            if len(self.inventory.equipment):
                self.transfer_equipment()
            self.equip_best_gear()
    def transfer_equipment(self):
        transferred_items = self.transfer_controller.transfer_items(self.inventory.equipment)
        return transferred_items
    def equip_best_gear(self):
        if self.leveler.run():
            self.vault.equip_best()
            for item in [self.inventory.weapon, self.inventory.armor, self.inventory.charm]:
                if item is not None:
                    try:
                        self.vault.deposit_item(item.name)
                    except:
                        pass
            self.inventory.load()
    def transmute_items(self):
        # check if any items are in the vault equipment spreadsheed
        # if so deposit it to the vault
        performed_transmute = self.transmuter.transmute_equipment(self.transmute_rank, self.inventory.equipment)
        if performed_transmute:
            self.update_transmute_rank()
    def enter_catacombs(self):
        self.controller.go('catacombs')
    def exit_catacombs(self):
        self.logger.info(f"{self.name}.exit_catacombs() --> Leaving Catacombs")
        self.controller.exit_catacombs()
    def update_health(self):
        self.health = self.controller.check_health()
    def update_transmute_rank(self):
        self.logger.info(f"{self.name}.update_transmute_rank() --> Checking player transmute level")
        self.controller.action.send_keys(Keys.SPACE).perform()
        self.controller.action.send_keys("p").perform()
        proficiencies_container_element = WebDriverWait(self.controller.driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'pbProfs'))
        )
        transmute_proficiency_element = WebDriverWait(proficiencies_container_element, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'profStat'))
        )[-2]
        self.transmute_rank = int(transmute_proficiency_element.text)
        self.controller.transmute_rank = int(transmute_proficiency_element.text)
        self.controller.action.send_keys(Keys.SPACE).perform()
    def explore(self, enter_health_percent, exit_health_percent):
        if self.health['percent'] != enter_health_percent: return False
        retreat = False
        self.controller.go('catacombs')
        while retreat == False:
            combat_occurred = False
            movement_direction = self.navigator.nav()
            self.controller.move(movement_direction)
            while True:
                self.update_health()
                # Pick up drops if there are any and get True/False result
                dropped_item_elements = self.controller.check_for_drops()
                if dropped_item_elements:
                    # work the list from back to front to preserve element order
                    dropped_item_elements.reverse()
                    for item_element in dropped_item_elements:
                        try:
                            item_overlay_stats = item_element.text.replace('+',"").split('\n')
                            if len(item_overlay_stats) == 1:
                                item_overlay_stats.insert(0, 0)
                        except StaleElementReferenceException:
                            self.logger.info(f"{self.name}explore --> StaleElementReferenceException: item_element became stale")
                            continue
                        if self.controller._should_pickup_drop(item_overlay_stats):
                            try:
                                item_element.click()
                            except StaleElementReferenceException:
                                self.logger.info(f"{self.name}explore --> StaleElementReferenceException: item disappeared before it could be picke up")
                    # If we picked something up the inventory might've become full
                    if self.inventory.is_full():
                        retreat = True
                        break
                if self.health['percent'] <= exit_health_percent:
                    retreat = True
                    break
                # if there are 9 mobs on screen likely they replicate too fast to be killed
                # joining and leaving a group will reset the catacombs and mobs
                active_mobs = self.controller.mobs_on_screen()
                # See if there are any mobs attacking the player
                if len(active_mobs) > 0:
                    mob_names = []
                    for name in active_mobs:
                        try:
                            mob_names.append(name.text)
                        except:
                            pass
                    # If this is the first time we've noticed the group attacking us
                    if combat_occurred == False:
                        # Show which mobs we are in battle with
                        combat_occurred = True
                    # use an ability if it is ready
                    self.controller.use_abilities()
                    # and attack them!
                    self.controller.attack_mob()
                else:
                    break
            # If the player saw combat
            if combat_occurred == True:
                # Get how much health is remaining
                self.health = self.controller.check_health()
                # then to re-engage with the maze
                self.controller.move("whistle")
        self.exit_catacombs()
        self.inventory.load()
        self.update_transmute_rank()
        return True
    def rest(self, stop_resting_health=100):
        while self.health['percent'] < stop_resting_health:
            self.update_health()
            sleep(.25)
    def do_master_quest(self):
        self.logger.info(f"{self.name}.do_master_quest()")
        try:
            self.controller.go("master_quest")
        except:
            self.logger.info(f"{self.name}.do_master_quest --> MasterQuest not available")
        attempt_quest_button = WebDriverWait(self.controller.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'mqAttempt')))
        attempt_quest_button.click()
        key_elements = WebDriverWait(self.controller.driver, 15).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mqKey')))
        door_element = WebDriverWait(self.controller.driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'mqDoorL')))
        key_element_to_use = choice(key_elements)
        ActionChains(self.controller.driver).drag_and_drop(key_element_to_use, door_element).perform()
#-----------------------------------------------
# Enigmatic Emblem className: "cEmblem"
# Chest className: "cChest"