using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;
using TqkLibrary.WpfUi;
using TqkLibrary.WpfUi.ObservableCollection;
using UploadYoutubeBot.Enums;

namespace UploadYoutubeBot.UI.ViewModels
{
    internal class MainWVM : BaseVM
    {
        public string BotId { get { return Setting.BotId.ToString(); } }


        bool _IsWorking = false;
        public bool IsWorking
        {
            get { return _IsWorking; }
            set { _IsWorking = value; NotifyPropertyChange(); }
        }
        public event Action<int> OnThreadCountChanged;
        public int ThreadCount
        {
            get { return Setting.ThreadCount; }
            set { Setting.ThreadCount = value; NotifyPropertyChange(); SaveSetting(); OnThreadCountChanged?.Invoke(value); }
        }

        SignalRConnectionState _ConnectionState = SignalRConnectionState.DisConnected;
        public SignalRConnectionState ConnectionState
        {
            get { return _ConnectionState; }
            set { _ConnectionState = value; NotifyPropertyChange(); }
        }


        public string ApiDomain
        {
            get { return Setting.ApiDomain; }
            set { Setting.ApiDomain = value; NotifyPropertyChange(); SaveSetting(); }
        }

        public YoutubeChannelVMSaveObservableCollection YoutubeChannels { get; }
            = new YoutubeChannelVMSaveObservableCollection();
        public IEnumerable<EnumVM<YoutubeChannelMenu>> YoutubeChannelMenus { get; } = new List<EnumVM<YoutubeChannelMenu>>()
        {
            new EnumVM<YoutubeChannelMenu>(YoutubeChannelMenu.OpenNonSelenium),
            null,
            new EnumVM<YoutubeChannelMenu>(YoutubeChannelMenu.CheckYoutubeProfile),

            null,
            new EnumVM<YoutubeChannelMenu>(YoutubeChannelMenu.AddProfile),
            new EnumVM<YoutubeChannelMenu>(YoutubeChannelMenu.AddProfileExist),
            new EnumVM<YoutubeChannelMenu>(YoutubeChannelMenu.DeleteSelectedProfile),

        };
        public LimitObservableCollection<string> Logs { get { return _Logs; } }

        private static readonly LimitObservableCollection<string> _Logs
            = new LimitObservableCollection<string>(() => Path.Combine(Singleton.LogDir, $"{DateTime.Now:yyyy-MM-dd HH}.log"));
        public static void WriteLog(string log, [CallerMemberName] string callFunction = null)
        {
            _Logs.Add($"{DateTime.Now:HH:mm:ss} [{callFunction}] {log}");
        }
        public static void WriteExceptionLog(string message, Exception ex, [CallerMemberName] string callFunction = null)
        {
            if (ex is AggregateException ae) ex = ae.InnerException;
            _Logs.Add($"{DateTime.Now:HH:mm:ss} [{callFunction}] [{message}] {ex.GetType().FullName}: {ex.Message}, {ex.StackTrace}");
        }
        public static void WriteExceptionLog(Exception ex, [CallerMemberName] string callFunction = null)
        {
            if (ex is AggregateException ae) ex = ae.InnerException;
            _Logs.Add($"{DateTime.Now:HH:mm:ss} [{callFunction}] {ex.GetType().FullName}: {ex.Message}, {ex.StackTrace}");
        }
    }
}
