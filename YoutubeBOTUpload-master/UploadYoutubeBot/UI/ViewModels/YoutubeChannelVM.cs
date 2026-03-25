using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TqkLibrary.WpfUi.ObservableCollection;
using TqkLibrary.WpfUi;
using UploadYoutubeBot.DataClass;
using System.Windows;
using System.Threading;

namespace UploadYoutubeBot.UI.ViewModels
{
    internal class YoutubeChannelVM : BaseVM, IViewModel<ProfileData>
    {
        public YoutubeChannelVM(ProfileData uploadConfigureData)
        {
            this.Data = uploadConfigureData;
            this.ChromeProfileVM = new ChromeProfileVM(this.Data);
            this.ChromeProfileVM.Change += (o, d) => SaveData();
        }

        public ProfileData Data { get; }
        public ChromeProfileVM ChromeProfileVM { get; }

        public event ChangeCallBack<ProfileData> Change;

        public void SaveData() => Change?.Invoke(this, Data);

        public string GroupName
        {
            get { return Data.GroupName; }
            set { Data.GroupName = value; NotifyPropertyChange(); SaveData(); }
        }
        public string ChannelId
        {
            get { return Data.ChannelId; }
            set { Data.ChannelId = value; NotifyPropertyChange(); SaveData(); }
        }
        public string ChannelName
        {
            get { return Data.ChannelName; }
            set { Data.ChannelName = value; NotifyPropertyChange(); SaveData(); }
        }
















        int _STT = 0;
        public int STT
        {
            get { return _STT; }
            set { _STT = value; NotifyPropertyChange(); }
        }

        Visibility _Visibility = Visibility.Visible;
        public Visibility Visibility
        {
            get { return _Visibility; }
            set { _Visibility = value; NotifyPropertyChange(); }
        }






        int _InWorkCount = 0;
        public int InWorkCount
        {
            get { return _InWorkCount; }
        }
        public void AddCount()
        {
            Interlocked.Add(ref _InWorkCount, 1);
            NotifyPropertyChange(nameof(InWorkCount));
        }
        public void SubtractCount()
        {
            Interlocked.Add(ref _InWorkCount, -1);
            NotifyPropertyChange(nameof(InWorkCount));
        }
    }
}
