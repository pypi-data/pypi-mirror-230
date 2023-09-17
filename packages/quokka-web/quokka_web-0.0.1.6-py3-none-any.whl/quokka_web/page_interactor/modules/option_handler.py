from quokka_web.page_interactor.modules.handler import Handler


class OptionHandler(Handler):
    async def select_option(self, scroll_down_sel: str, value: str, **kwargs):
        """
        Select an option from the dropdown list.

        :param scroll_down_sel: (str) the selector of the dropdown list
        :param value: (str) the option to be selected
        :return:
        """
        return await self.page.select_option(selector=scroll_down_sel, value=value, **kwargs)


__all__ = ['OptionHandler']
