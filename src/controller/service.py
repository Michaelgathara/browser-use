from src.browser.service import BrowserService
from src.browser.views import BrowserState
from src.controller.views import ControllerActionResult, ControllerActions, ControllerPageState


class ControllerService:
	"""
	Controller service that interacts with the browser.

	Right now this is just a LLM friendly wrapper around the browser service.
	In the future we can add the functionality that this is a self-contained agent that can plan and act single steps.

	TODO: easy hanging fruit: pass in a list of actions, compare html that changed and self assess if goal is done -> makes clicking MUCH MUCH faster and cheaper.

	TODO#2: from the state generate functions that can be passed directly into the LLM as function calls. Then it could actually in the same call request for example multiple actions and new state.
	"""

	def __init__(self):
		self.browser = BrowserService()
		self.cached_browser_state: BrowserState | None = None

	def get_cached_browser_state(self, force_update: bool = False) -> BrowserState:
		if self.cached_browser_state is None or force_update:
			self.cached_browser_state = self.browser.get_updated_state()

		return self.cached_browser_state

	def get_current_state(self, screenshot: bool = False) -> ControllerPageState:
		browser_state = self.get_cached_browser_state(force_update=True)

		screenshot_b64 = None
		if screenshot:
			screenshot_b64 = self.browser.take_screenshot()

		return ControllerPageState(
			items=browser_state.items,
			url=browser_state.url,
			title=browser_state.title,
			selector_map=browser_state.selector_map,
			screenshot=screenshot_b64,
		)

	def act(self, action: ControllerActions) -> ControllerActionResult:
		try:
			if action.search_google:
				self.browser.search_google(action.search_google.query)
			elif action.go_to_url:
				self.browser.go_to_url(action.go_to_url.url)
			elif action.nothing:
				# self.browser.nothing()
				# TODO: implement
				pass
			elif action.go_back:
				self.browser.go_back()
			elif action.done:
				return ControllerActionResult(done=True)
			elif action.click_element:
				self.browser.click_element_by_index(
					action.click_element.id, self.get_cached_browser_state()
				)
			elif action.input_text:
				self.browser.input_text_by_index(
					action.input_text.id, action.input_text.text, self.get_cached_browser_state()
				)
			elif action.extract_page_content:
				content = self.browser.extract_page_content()
				return ControllerActionResult(done=False, extracted_content=content)
			else:
				raise ValueError(f'Unknown action: {action}')

			return ControllerActionResult(done=False)

		except Exception as e:
			return ControllerActionResult(done=False, error=str(e))