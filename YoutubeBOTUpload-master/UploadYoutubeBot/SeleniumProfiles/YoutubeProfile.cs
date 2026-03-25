using OpenQA.Selenium;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.Remoting;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using TqkLibrary.SeleniumSupport;
using TqkLibrary.SeleniumSupport.Helper.WaitHeplers;
using UploadYoutubeBot.DataClass;
using UploadYoutubeBot.Enums;
using UploadYoutubeBot.Exceptions;
using UploadYoutubeBot.Interfaces;
using UploadYoutubeBot.UI.ViewModels;

namespace UploadYoutubeBot.SeleniumProfiles
{
    internal class YoutubeProfile : ChromeProfile
    {
        const int timeout = 20000;
        public YoutubeProfile(ChromeProfileVM chromeProfileVM) : base(chromeProfileVM)
        {
        }

        static readonly Regex regex_channelid = new Regex("(?<=channel\\/).+");

        internal async Task<ChannelInfo> GetChannelIdAsync(string proxy = null, CancellationToken cancellationToken = default)
        {
            if (!IsOpenChrome) await OpenChromeAsync();
            chromeDriver.Navigate().GoToUrl("https://www.youtube.com/");

            var waiter = new WaitHelper(this, cancellationToken);
            waiter.DefaultTimeout = timeout;

            await waiter.WaitUntilElements("body").Until().ElementsExists().WithThrow().StartAsync();
            await DelayAsync(500, cancellationToken);
            chromeDriver.Manage().Cookies.AddCookie(new Cookie("PREF", "f6=40000000&tz=Asia.Bangkok&hl=en", ".youtube.com", "/", DateTime.Now.AddYears(2), true, false, ""));
            //chromeDriver.ExecuteScript("var lines = document.cookie.split('; ');var newLines = [];lines.forEach(x => {if(!x.startsWith('PREF'))newLines.push(x)});newLines.push('f6=40000000&tz=Asia.Bangkok&hl=en');document.cookie = newLines.join('; ');");
            var avatar_btn = await waiter.WaitUntilElements("#avatar-btn").Until().AnyElementsVisible().WithThrow().StartAsync().FirstAsync();
            var avatar = await waiter.WaitUntilElements("#avatar-btn img#img[src^='http']").WithTimeout(2000).Until().AnyElementsVisible().StartAsync().FirstOrDefaultAsync();
            var avatar_url = avatar?.GetAttribute("src");

            avatar_btn.Click();

            IWebElement webElement = await waiter.WaitUntilElements("#contentWrapper:has(#account-name)").WithThrow().Until().ElementsExists().StartAsync().FirstAsync();
            await DelayAsync(500, cancellationToken);

            var accountName = await waiter.WaitUntilElements("#contentWrapper #account-name").WithThrow().Until().ElementsExists().StartAsync().FirstAsync();
            var email = await waiter.WaitUntilElements("#contentWrapper:has(#account-name) #email").WithThrow().Until().ElementsExists().StartAsync().FirstAsync();
            var endpoint = await waiter.WaitUntilElements("#contentWrapper:has(#account-name) :is(#endpoint[href*='/channel/'],a.yt-simple-endpoint[href*='/channel/'])").WithThrow().Until().ElementsExists().StartAsync().FirstAsync();
            string href = endpoint.GetAttribute("href");
            var m_href = regex_channelid.Match(href);

            return new ChannelInfo()
            {
                ChannelId = m_href.Value,
                Email = email?.Text,
                ChannelName = accountName?.Text,
                AvatarUrl = avatar_url,
            };
        }

        static readonly Regex regex_email = new Regex("\\((.*?)\\)");
        internal async Task<string> GetGmailAsync(string proxy = null, CancellationToken cancellationToken = default)
        {

            if (!IsOpenChrome) await OpenChromeAsync();
            chromeDriver.Navigate().GoToUrl("https://myaccount.google.com/");

            var waiter = new WaitHelper(this, cancellationToken);
            waiter.DefaultTimeout = timeout;

            await waiter.WaitUntilElements("body").WithThrow().Until().ElementsExists().StartAsync();

            var logout = chromeDriver.FindElements(By.CssSelector("a[href*='SignOutOptions']")).FirstOrDefault();
            string aria_label = logout?.GetAttribute("aria-label");
            if (!string.IsNullOrWhiteSpace(aria_label))
            {
                Match match = regex_email.Match(aria_label);
                if (match.Success)
                {
                    return match.Groups[1].Value;
                }
            }
            return string.Empty;
        }
        //<ytcp-video-upload-progress class="style-scope ytcp-uploads-dialog" hd-etas-enabled="" checks-summary-status-v2="UPLOAD_CHECKS_DATA_SUMMARY_STATUS_NOT_STARTED" uploading="">
        //<span class="progress-label style-scope ytcp-video-upload-progress">Đã tải được 27% ... Còn 35 giây</span>

        //<ytcp-video-upload-progress class="style-scope ytcp-uploads-dialog" hd-etas-enabled="" checks-summary-status-v2="UPLOAD_CHECKS_DATA_SUMMARY_STATUS_NOT_STARTED" processing="">
        //<span class="progress-label style-scope ytcp-video-upload-progress">Đang kiểm tra 1% ... Còn 10 phút</span>

        //<ytcp-video-upload-progress class="style-scope ytcp-uploads-dialog" hd-etas-enabled="" checks-summary-status-v2="UPLOAD_CHECKS_DATA_SUMMARY_STATUS_STARTED" checks-can-start="" pulse-checks-badge="">
        //<span class="progress-label style-scope ytcp-video-upload-progress">Đang kiểm tra 5% ... Còn 10 phút</span>
        internal async Task<string> YoutubeUploadAsync(
            IVideoUploadInfo videoUploadInfo,
            Action<int> uploadProgressCallback = null,
            string proxy = null,
            CancellationToken cancellationToken = default
            )
        {
            string UrlResult = String.Empty;
            if (string.IsNullOrEmpty(videoUploadInfo?.VideoPath)) throw new ArgumentNullException(nameof(videoUploadInfo));
            if (!File.Exists(videoUploadInfo.VideoPath)) throw new FileNotFoundException(videoUploadInfo.VideoPath);

            if (!IsOpenChrome) await OpenChromeAsync();
            chromeDriver.Manage().Window.Size = new System.Drawing.Size(1000, 600);

            var waiter = new WaitHelper(this, cancellationToken);
            waiter.DefaultTimeout = timeout;
            waiter.Do(Check);

            chromeDriver.Navigate().GoToUrl($"https://studio.youtube.com/channel/{chromeProfileVM.Data.ChannelId}/videos?d=ud");

            WriteLog($"Upload {videoUploadInfo.VideoPath}");
            await waiter
                .WaitUntilElements(By.Name("Filedata"))
                .Until().ElementsExists()
                .WithThrow()
                .StartAsync()
                .FirstAsync()
                .SendKeysAsync(videoUploadInfo.VideoPath);

            while (true)
            {
                var ele_ = await waiter
                    .WaitUntilElements(By.ClassName("video-url-fadeable"))
                    .WithThrow()
                    .Until().ElementsExists()
                    .WithTimeout(30000)
                    .StartAsync()
                    .FirstAsync();
                UrlResult = ele_.Text;
                if (!string.IsNullOrWhiteSpace(UrlResult?.Trim())) break;
                await DelayAsync(500, 500);
            }
            WriteLog($"Video url: {UrlResult}");

            Task task_uploadProgress = GetProgressAsync(uploadProgressCallback, cancellationToken);

            //Details tab
            Check();
            if (File.Exists(videoUploadInfo.ThumbPath))
            {
                WriteLog($"Set Thumb Image {videoUploadInfo.ThumbPath}");
                if (chromeDriver.FindElements(By.CssSelector("ytcp-thumbnails-compact-editor-uploader[feature-disabled]")).Count > 0)
                {
                    WriteLog($"Thumbnails feature-disabled on this account");
                }
                else
                {
                    await waiter
                        .WaitUntilElements("div[id='still-picker'] input[id='file-loader']")
                        .WithThrow()
                        .Until()
                        .ElementsExists()
                        .StartAsync()
                        .FirstAsync()
                        .SendKeysAsync(videoUploadInfo.ThumbPath);
                }
            }

            if (videoUploadInfo?.PlayList is not null && videoUploadInfo.PlayList.Count > 0)
            {
                JsClick(await waiter
                    .WaitUntilElements("ytcp-text-dropdown-trigger[class*='ytcp-video-metadata-playlists']")
                    .WithThrow()
                    .Until().AnyElementsClickable()
                    .StartAsync()
                    .FirstAsync());
                var eles = await waiter
                    .WaitUntilElements("tp-yt-paper-dialog[class*='ytcp-playlist-dialog'] ytcp-checkbox-group[id='playlists-list'] ytcp-ve[class*='ytcp-checkbox-group']")
                    .WithThrow()
                    .Until().ElementsExists()
                    .StartAsync();
                eles = await waiter
                    .WaitUntilElements("tp-yt-paper-dialog[class*='ytcp-playlist-dialog'] ytcp-checkbox-group[id='playlists-list'] ytcp-ve[class*='ytcp-checkbox-group']")
                    .WithThrow()
                    .Until().ElementsExists()
                    .StartAsync();
                foreach (var ele in eles)
                {
                    string PlayListName = ele.Text.Trim();
                    if (videoUploadInfo.PlayList.Any(x => x.Equals(PlayListName, StringComparison.OrdinalIgnoreCase)))
                    {
                        WriteLog($"Set playlist {PlayListName}");
                        var ele2 = ele.FindElements(By.CssSelector("ytcp-checkbox-lit")).FirstOrDefault();
                        if (ele2 != null) JsClick(ele2);
                    }
                }

                JsClick(await waiter
                    .WaitUntilElements("tp-yt-paper-dialog[class*='ytcp-playlist-dialog'] ytcp-button[class*='done-button']")
                    .WithThrow()
                    .Until().AnyElementsClickable()
                    .StartAsync()
                    .FirstAsync());
            }

            WriteLog($"Set KIDS: {videoUploadInfo.IsMakeForKid}");
            //old ver MADE_FOR_KIDS
            //new ver VIDEO_MADE_FOR_KIDS_MFK
            if (videoUploadInfo.IsMakeForKid)
                JsClick(await waiter
                    .WaitUntilElements("tp-yt-paper-radio-button:is([name='MADE_FOR_KIDS'],[name='VIDEO_MADE_FOR_KIDS_MFK'])")
                    .WithThrow()
                    .Until().AllElementsClickable()
                    .StartAsync()
                    .FirstAsync());
            else JsClick(await waiter
                .WaitUntilElements("tp-yt-paper-radio-button:is([name='NOT_MADE_FOR_KIDS'],[name='VIDEO_MADE_FOR_KIDS_NOT_MFK'])")
                    .WithThrow()
                    .Until().AllElementsClickable()
                    .StartAsync()
                    .FirstAsync());

            //open advance
            JsClick(await waiter
                .WaitUntilElements("ytcp-button[id='toggle-button'][class*='ytcp-video-metadata-editor']")
                .WithThrow()
                .Until().ElementsExists()
                .StartAsync()
                .FirstAsync());

            if (!string.IsNullOrWhiteSpace(videoUploadInfo.Tags))
            {
                while (true)
                {
                    var ele = chromeDriver.FindElements(By.CssSelector("#tags-container ytcp-chip>ytcp-icon-button#delete-icon")).FirstOrDefault();
                    if (ele == null) break;
                    JsClick(ele);
                }
                WriteLog($"Set tags {videoUploadInfo.Tags}");
                await waiter
                    .WaitUntilElements("ytcp-form-input-container[id='tags-container'] input[id='text-input']")
                    .WithThrow()
                    .Until().ElementsExists()
                    .StartAsync()
                    .FirstAsync()
                    .SendKeysAsync(videoUploadInfo.Tags);
            }

            Check();
            if (!string.IsNullOrEmpty(videoUploadInfo.Title))
            {
                if (videoUploadInfo.Title.Length > 100) throw new Exception("Tiêu đề dài hơn 100 ký tự");
                WriteLog($"Set title {videoUploadInfo.Title}");
                var ele = await waiter
                    .WaitUntilElements("ytcp-social-suggestions-textbox[id='title-textarea'] :is(ytcp-social-suggestion-input,ytcp-mention-input)[id='input'] div[id='textbox']")
                    .Until().AnyElementsClickable()
                    .WithThrow()
                    .StartAsync()
                    .FirstAsync();
                JsClick(ele);
                ele.Clear();
                ele.SendKeys(videoUploadInfo.Title);
            }

            Check();
            if (!string.IsNullOrEmpty(videoUploadInfo.Description))
            {
                WriteLog($"Set description {videoUploadInfo.Description}");
                var ele = await waiter
                    .WaitUntilElements("div[id='description-container'] :is(ytcp-social-suggestion-input,ytcp-mention-input)[id='input'] div[id='textbox']")
                    .WithThrow()
                    .Until().AnyElementsClickable()
                    .StartAsync()
                    .FirstAsync();
                JsClick(ele);
                ele.Clear();
                ele.SendKeys(videoUploadInfo.Description);
            }

            Check();
            if (!videoUploadInfo.IsDraft)
            {
                //Review tab
                JsClick(await waiter
                    .WaitUntilElements("button[id='step-badge-3'][test-id='REVIEW']")
                    .WithThrow()
                    .Until().AnyElementsClickable()
                    .StartAsync()
                    .FirstAsync());
                switch (videoUploadInfo.VideoPrivacyStatus)
                {
                    case VideoPrivacyStatus.PUBLIC:
                        {
                            WriteLog($"Set Privacy: {videoUploadInfo.VideoPrivacyStatus}");
                            JsClick(await waiter
                                .WaitUntilElements(By.Name(videoUploadInfo.VideoPrivacyStatus.ToString()))
                                .WithThrow()
                                .Until().AllElementsClickable()
                                .StartAsync()
                                .FirstAsync());
                            if (videoUploadInfo.Premiere)
                            {
                                WriteLog($"Set premiere");
                                JsClick(await waiter
                                    .WaitUntilElements(By.Id("enable-premiere-checkbox"))
                                    .WithThrow()
                                    .Until().AllElementsClickable()
                                    .StartAsync()
                                    .FirstAsync());
                            }
                            break;
                        }
                    case VideoPrivacyStatus.SCHEDULE:
                        {
                            if (videoUploadInfo.Schedule is not null && videoUploadInfo.Schedule > DateTime.Now.AddMinutes(1))
                            {
                                JsClick(await waiter.WaitUntilElements(By.Name(VideoPrivacyStatus.SCHEDULE.ToString())).WithThrow().Until().AllElementsClickable().StartAsync().FirstAsync());
                                JsClick(await waiter.WaitUntilElements("ytcp-text-dropdown-trigger[id='datepicker-trigger']").WithThrow().Until().AnyElementsClickable().StartAsync().FirstAsync());
                                var ele = await waiter.WaitUntilElements("tp-yt-paper-dialog[class*='ytcp-date-picker'] input[class*='tp-yt-paper-input']").WithThrow().Until().AnyElementsClickable().StartAsync().FirstAsync();
                                JsClick(ele);
                                ele.Clear();
                                string day = videoUploadInfo.Schedule.Value.ToString("MM/dd/yyyy");
                                ele.SendKeys(day + "\r\n");
                                WriteLog($"Set SCHEDULE: Day:{day}");

                                ele = await waiter.WaitUntilElements("#time-of-day-container input").WithThrow().Until().AnyElementsClickable().StartAsync().FirstAsync();
                                JsClick(ele);
                                ele.Clear();
                                string time = videoUploadInfo.Schedule.Value.ToString("HH:mm");
                                ele.SendKeys(time + "\r\n");
                                WriteLog($"Set SCHEDULE: Time:{time}");

                                if (videoUploadInfo.Premiere)
                                {
                                    WriteLog($"Set premiere");
                                    JsClick(await waiter.WaitUntilElements(By.Id("schedule-type-checkbox")).WithThrow().Until().AllElementsClickable().StartAsync().FirstAsync());
                                }
                            }
                            else//public now
                            {
                                WriteLog($"Set Privacy: {videoUploadInfo.VideoPrivacyStatus}");
                                JsClick(await waiter.WaitUntilElements(By.Name(VideoPrivacyStatus.PUBLIC.ToString())).WithThrow().Until().AllElementsClickable().StartAsync().FirstAsync());
                                if (videoUploadInfo.Premiere)
                                {
                                    WriteLog($"Set premiere");
                                    JsClick(await waiter.WaitUntilElements(By.Id("enable-premiere-checkbox")).WithThrow().Until().AllElementsClickable().StartAsync().FirstAsync());
                                }
                            }
                            break;
                        }

                    case VideoPrivacyStatus.PRIVATE:
                    case VideoPrivacyStatus.UNLISTED:
                        WriteLog($"Set Privacy: {videoUploadInfo.VideoPrivacyStatus}");
                        JsClick(await waiter
                            .WaitUntilElements(By.Name(videoUploadInfo.VideoPrivacyStatus.ToString()))
                            .WithThrow()
                            .Until().AllElementsClickable()
                            .StartAsync()
                            .FirstAsync());
                        break;

                    default:
                        break;
                }
            }

            await task_uploadProgress;

            if (!videoUploadInfo.IsDraft)
            {
                JsClick(
                    await waiter
                    .WaitUntilElements("tp-yt-paper-dialog[class*='ytcp-uploads-dialog'] ytcp-button[id='done-button']")
                    .WithThrow()
                    .Until().AnyElementsClickable()
                    .StartAsync()
                    .FirstAsync());
            }

            await DelayAsync(2000);
            WriteLog($"Upload Hoàn tất");
            return UrlResult;
        }

        async Task GetProgressAsync(
            Action<int> uploadProgressCallback = null,
            CancellationToken cancellationToken = default
            )
        {
            Regex regex_num = new Regex("\\d+");

            var waiter = new WaitHelper(this, cancellationToken);
            waiter.Do(Check);
            waiter.DefaultTimeout = timeout;
            await waiter.WaitUntilElements(".ytcp-uploads-dialog ytcp-video-upload-progress[uploading]").Until().ElementsExists().StartAsync();

            while (chromeDriver.FindElements(By.CssSelector(".ytcp-uploads-dialog ytcp-video-upload-progress[uploading]")).Count > 0)
            {
                string progress = chromeDriver.FindElements(By.CssSelector(".ytcp-uploads-dialog span.ytcp-video-upload-progress")).FirstOrDefault()?.Text?.Trim();
                if (!string.IsNullOrWhiteSpace(progress))
                {
                    WriteLog($"Upload: {progress}");
                    if (uploadProgressCallback is not null)
                    {
                        Match match = regex_num.Match(progress);
                        if (match.Success)
                        {
                            uploadProgressCallback.Invoke(int.Parse(match.Value));
                        }
                    }
                }
                Check();
                await DelayAsync(500);
                cancellationToken.ThrowIfCancellationRequested();
            }
            Check();
        }
        void Check()
        {
            var eles = chromeDriver.FindElements("ytcp-auth-confirmation-dialog");
            if (eles.Count > 0)
                throw new YtcpAuthConfirmationDialogException();

            eles = chromeDriver.FindElements("ytcp-uploads-dialog[has-error]");
            if (eles.Count > 0)
                throw new Exception($"{chromeDriver.FindElements("ytcp-uploads-dialog[has-error] .error-short").FirstOrDefault()?.Text}");
        }
    }
}
