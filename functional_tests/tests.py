from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from unittest import TestCase
import unittest
import time

class NewVisitorTest(LiveServerTestCase):
	
	def setUp(self):
		self.browser = webdriver.Firefox()
	
	def tearDown(self):
		self.browser.quit()

	def check_for_row_in_list_table(self, row_text):
		table = self.browser.find_element_by_id('id_list_table')
		rows = table.find_elements_by_tag_name('tr')
		self.assertIn(row_text, [row.text for row in rows])

	def test_start_list_and_retrieve_it(self):
		self.browser.get(self.live_server_url)
		
		self.assertIn('To-Do', self.browser.title)
		header_text = self.browser.find_element_by_tag_name('h1').text
		self.assertIn('To-Do', header_text)

		inputbox = self.browser.find_element_by_id('id_new_item')
		self.assertEqual(
			inputbox.get_attribute('placeholder'),
			'Enter a to-do item',
		)

		#list entered for first user, first URL created
		inputbox.send_keys('Buy peacock feathers')
		inputbox.send_keys(Keys.ENTER)
		first_list_url = self.browser.current_url

		#calls helper function from unittest to check whether string matches regex
		self.assertRegex(first_list_url, 'lists/.+')
		time.sleep(1)
		self.check_for_row_in_list_table('1: Buy peacock feathers')

		inputbox = self.browser.find_element_by_id('id_new_item')
		inputbox.send_keys('Use peacock feathers to make a fly')
		inputbox.send_keys(Keys.ENTER)
		time.sleep(1)

		#checks items are displayed in list
		self.check_for_row_in_list_table('2: Use peacock feathers to make a fly')
		self.check_for_row_in_list_table('1: Buy peacock feathers')

		#checking new user sees fresh page
		#resets cookies etc
		self.browser.quit()
		self.browser = webdriver.Firefox()

		#test to see if list not left over from previous user
		self.browser.get(self.live_server_url)
		page_text = self.browser.find_elements_by_tag_name('body').text
		self.assertNotIn('Buy peacock feathers', page_text)
		self.assertNotIn('make a fly', page_text)

		#create new list in 2nd URL
		inputbox = self.browser.find_element_by_id('id_new_item')
		inputbox.send_keys('buy milk')
		inputbox.send_keys(keys.ENTER)
		second_list_url = self.browser.current_url
		self.assertRegex(second_list_url, '/lists/.+')

		#check the two created URLs are not the same
		self.assertNotEqual(first_list_url, second_list_url)

		#first list still not around
		page_text = self.browser.find_elements_by_tag_name('body').text
		self.assertNotIn('Buy peacock feathers', page_text)
		self.assertIn('Buy milk', page_text)

		#tests not finished yet
		self.fail('finish the test')


if __name__ == '__main__':
	unittest.main(warnings='ignore')