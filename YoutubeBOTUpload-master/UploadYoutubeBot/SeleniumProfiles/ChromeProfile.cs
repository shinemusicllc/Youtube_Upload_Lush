using Nito.AsyncEx;
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using TqkLibrary.SeleniumSupport;
using TqkLibrary.SeleniumSupport.Helper;
using TqkLibrary.SeleniumSupport.Helper.WaitHeplers;
using UploadYoutubeBot.Exceptions;
using UploadYoutubeBot.UI.ViewModels;

namespace UploadYoutubeBot.SeleniumProfiles
{
    internal class ChromeProfile : BaseChromeProfile
    {
        protected readonly ChromeProfileVM chromeProfileVM;
        public ChromeProfile(ChromeProfileVM chromeProfileVM) : base(Singleton.ChromeDriverDir)
        {
            this.chromeProfileVM = chromeProfileVM ?? throw new ArgumentNullException(nameof(chromeProfileVM));
        }
        public event Action<string> LogCallback;
        protected void WriteLog(string log)
        {
            LogCallback?.Invoke($"[{chromeProfileVM.ProfileName}] {log}");
        }

        static readonly AsyncLock asyncLock = new AsyncLock();
        protected async Task<ChromeOptions> InitChromeOptionsAsync(string proxy = null)
        {
            using (await asyncLock.LockAsync())
            {
                Singleton.Setting.Setting.ChromeVer = await ChromeDriverUpdater.DownloadAsync(Singleton.ChromeDriverDir, Singleton.Setting.Setting.ChromeVer);
                Singleton.Setting.Save();
            }

            ChromeOptions chromeOptions = DefaultChromeOptions();
            //chromeOptions.AddUserAgent(UserAgentHelper.GetRandomUa());
            chromeOptions.AddProfilePath($"{Singleton.ProfilesDir}\\{chromeProfileVM.ProfileName}");
            try
            {
                string dir = $"{Singleton.ProfilesDir}\\{chromeProfileVM.ProfileName}\\Default\\Extensions";
                if (Directory.Exists(dir))
                    Directory.Delete(dir, true);
            }
            catch { }
            if (!string.IsNullOrWhiteSpace(proxy))
            {
                var splits = proxy.Trim().Split(':');
                if (splits.Length == 4)
                {
                    ProxyLoginExtension.GenerateExtension(Path.Combine(Singleton.ProfilesDir, $"{chromeProfileVM.ProfileName}.zip"),
                        splits[0], splits[1], splits[2], splits[3], true);
                    chromeOptions.AddExtension($"{Singleton.ProfilesDir}\\{chromeProfileVM.ProfileName}.zip");
                }
                else if (splits.Length == 2) chromeOptions.AddProxy(proxy.Trim());
            }
            return chromeOptions;
        }

        public async Task OpenChromeAsync(string proxy = null)
        {
            OpenChrome(await InitChromeOptionsAsync(proxy));
            //chromeDriver.Manage().Window.Size = new System.Drawing.Size(1000, 600);
            if (chromeDriver is null)
                throw new CanNotOpenChromeException();
        }
        public new bool IsOpenProcess { get { return base.IsOpenChrome && process != null; } }
        public void OpenHand(string proxy = null)
        {
            List<string> args = new List<string>()
            {
                $"\"--user-data-dir={Path.Combine(Singleton.ProfilesDir,chromeProfileVM.ProfileName)}\"",
            };
            if (!string.IsNullOrWhiteSpace(proxy))
            {
                var splits = proxy.Trim().Split(':');
                if (splits.Length == 4)
                {
                    ProxyLoginExtension.GenerateExtension(Path.Combine(Singleton.ProfilesDir, $"{chromeProfileVM.ProfileName}_proxyExt"),
                        splits[0], splits[1], splits[2], splits[3], false);
                    args.Add($"--load-extension=\"{Singleton.ProfilesDir}\\{chromeProfileVM.ProfileName}_proxyExt\"");
                }
                else if (splits.Length == 2) args.Add($"--proxy-server=\"http://{proxy.Trim()}\"");
            }
            args.Add("\"https://www.youtube.com/\"");
            OpenChromeWithoutSelenium(string.Join(" ", args));
        }


        public async Task DeleteIndexedDB()
        {
            if (IsOpenChrome)
            {
                CloseChrome();
                await DelayAsync(1000);
            }
            try
            {
                Directory.Delete(Path.Combine(chromeProfileVM.ProfileDir, "Default", "IndexedDB"), true);
            }
            catch
            {

            }
        }

        public async Task HoldOnChromeOpenAsync(CancellationToken cancellationToken = default)
        {
            var waiter = new WaitHelper(this, cancellationToken);
            waiter.DefaultTimeout = 10000;
            while (true)
            {
                try
                {
                    await waiter.WaitUntilElements("body").Until().ElementsExists().WithThrow().StartAsync();//exception on close chrome
                    await DelayAsync(1000, cancellationToken);
                }
                catch (Exception ex)
                {
                    if (ex is AggregateException ae) ex = ae.InnerException;
                    if (ex is NoSuchWindowException) break;
                    if (ex is OperationCanceledException) throw;
                    WriteLog($"{ex.GetType().FullName}: {ex.Message}, {ex.StackTrace}");
                }
            }
        }
    }
}
