from browser_use import Browser
from browser_use.browser.events import BrowserStateRequestEvent, NavigationCompleteEvent
from browser_use.browser.watchdogs.downloads_watchdog import DownloadsWatchdog


class PatchedBrowser(Browser):
    async def attach_all_watchdogs(self) -> None:
        await super().attach_all_watchdogs()
        await self._patch_downloaded_watchdog()

    async def _patch_downloaded_watchdog(self) -> None:
        del self._downloads_watchdog

        PatchedDownloadsWatchdog.model_rebuild()

        self._downloads_watchdog = PatchedDownloadsWatchdog(
            event_bus=self.event_bus,
            browser_session=self,
        )
        self._downloads_watchdog.attach_to_session()


class PatchedDownloadsWatchdog(DownloadsWatchdog):
    LISTENS_TO = DownloadsWatchdog.LISTENS_TO + [BrowserStateRequestEvent]

    async def on_BrowserStateRequestEvent(self, event: BrowserStateRequestEvent):
        cdp_session = self.browser_session.agent_focus
        if not cdp_session:
            return

        page_url = await self.browser_session.get_current_page_url()
        if not page_url:
            return

        # Mock NavigationCompleteEvent
        self.event_bus.dispatch(
            NavigationCompleteEvent(
                event_parent_id=event.event_id,
                event_type="NavigationCompleteEvent",
                target_id=cdp_session.target_id,
                url=page_url,
            )
        )
