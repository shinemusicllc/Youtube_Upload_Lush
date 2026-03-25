using BaseSource.SharedSignalrData.Classes;
using BaseSource.SharedSignalrData.Enums;
using Nito.AsyncEx;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Timers;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using TqkLibrary.Queues.TaskQueues;
using TqkLibrary.WpfUi.UserControls;
using UploadYoutubeBot.DataClass;
using UploadYoutubeBot.Enums;
using UploadYoutubeBot.Helpers;
using UploadYoutubeBot.Interfaces;
using UploadYoutubeBot.Services;
using UploadYoutubeBot.UI.ViewModels;
using UploadYoutubeBot.Works;
using Xceed.Wpf.Toolkit.Primitives;

namespace UploadYoutubeBot.UI
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        SignalrClient _signalrClient;
        readonly MainWVM _mainWVM;
        readonly ISystemInfoReader _systemInfoReader = new WindowSystemInfoReader();
        readonly System.Timers.Timer _timer_clearLog = new System.Timers.Timer(60000);
        readonly System.Timers.Timer _timer_updateChannel = new System.Timers.Timer(2000);
        readonly ScheduleService<MainWork> _scheduleServiceMainWork;
        readonly System.Timers.Timer _timer_ping = new System.Timers.Timer(2000);
        readonly WorkQueue<BaseWork> _works = new WorkQueue<BaseWork>();
        public MainWindow()
        {
            var a = new Uri("https://1drv.ms/f/s!AqsZzkUJtHuHjF1K1mTHekJ4hBY4?e=JzJX9W");
            if (System.IO.Directory.GetCurrentDirectory().StartsWith(System.IO.Path.GetTempPath()))
            {
                MessageBox.Show("Hãy giải nén ra để chạy", "Thông báo");
                Environment.Exit(-1);
            }
            Singleton.Setting.OnSaved += Setting_OnSaved;
            try
            {
                Directory.Delete(Singleton.BaseWorkingDir, true);
            }
            catch
            {

            }
            finally
            {
                Directory.CreateDirectory(Singleton.BaseWorkingDir);
            }
            InitializeComponent();
            this._mainWVM = this.DataContext as MainWVM;
            this._mainWVM.YoutubeChannels.OnProfilesChanged += YoutubeChannels_OnProfilesChanged;
            this._mainWVM.OnThreadCountChanged += _mainWVM_OnThreadCountChanged;

            _timer_updateChannel.AutoReset = false;
            _timer_updateChannel.Elapsed += Timer_updateChannel_Elapsed;

            _timer_clearLog.AutoReset = true;
            _timer_clearLog.Elapsed += _timer_clearLog_Elapsed;
            _timer_clearLog.Start();

            _scheduleServiceMainWork = new ScheduleService<MainWork>(AddQueueMainWork);

            _timer_ping.AutoReset = true;
            _timer_ping.Elapsed += _timer_ping_Elapsed;

            _works.SetRunLockObject(x => x.YoutubeChannel);
            _works.OnWorkComplete += _works_OnWorkComplete;
            _works.MaxRun = _mainWVM.ThreadCount;
        }

        private Task _works_OnWorkComplete(Task task, WorkEventArgs<BaseWork> workEventArgs)
        {
            UpdateQueueIndex();
            return Task.CompletedTask;
        }

        private void Setting_OnSaved(SettingData settingData)
        {
            try
            {
                _signalrClient?.ServerHub?.BotConfigResponseAsync(new BotConfig()
                {
                    ThreadCount = settingData.ThreadCount,
                });
            }
            catch (Exception ex)
            {
                MainWVM.WriteExceptionLog(ex);
            }
        }

        private void _timer_clearLog_Elapsed(object sender, ElapsedEventArgs e)
        {
            try
            {
                var fileInfos = Directory.GetFiles(Singleton.LogDir).Select(x => new FileInfo(x)).ToArray();
                DateTime dateTime = DateTime.Now.AddDays(-7);
                foreach (var fileInfo in fileInfos)
                {
                    if (fileInfo.CreationTime < dateTime)
                    {
                        fileInfo.Delete();
                    }
                }
            }
            catch (Exception ex)
            {
                MainWVM.WriteExceptionLog(ex);
            }
        }

        private void _timer_ping_Elapsed(object sender, ElapsedEventArgs e)
        {
            if (_signalrClient?.ServerHub is not null)
            {
                try
                {
                    DriveInfo driveInfo = DriveInfo.GetDrives().FirstOrDefault(x => x.Name.Equals(Singleton.ExeDirInfo.Root.Name));
                    if (driveInfo is not null)
                    {
                        PingData pingData = new PingData();
                        pingData.StorageTotal = driveInfo.TotalSize;
                        pingData.StorageCurrent = driveInfo.TotalSize - driveInfo.AvailableFreeSpace;
                        pingData.Bandwidth = _systemInfoReader.GetBandwidth();
                        _signalrClient?.ServerHub?.PingAsync(pingData);
                    }
                }
                catch (Exception ex)
                {
                    MainWVM.WriteExceptionLog(ex);
                }
            }
        }

        private void _mainWVM_OnThreadCountChanged(int obj)
        {
            this._works.MaxRun = obj;
        }

        private void SearchUC_SearchTextChange(string obj)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(obj))
                {
                    foreach (var item in _mainWVM.YoutubeChannels) item.Visibility = Visibility.Visible;
                }
                else
                {
                    foreach (var item in _mainWVM.YoutubeChannels)
                    {
                        if ((!string.IsNullOrWhiteSpace(item.ChromeProfileVM.ChannelName) &&
                            item.ChromeProfileVM.ChannelName.IndexOf(obj, StringComparison.OrdinalIgnoreCase) >= 0) ||
                            (!string.IsNullOrWhiteSpace(item.ChromeProfileVM.Email) &&
                            item.ChromeProfileVM.Email.IndexOf(obj, StringComparison.OrdinalIgnoreCase) >= 0))
                        {
                            item.Visibility = Visibility.Visible;
                        }
                        else
                        {
                            item.Visibility = Visibility.Collapsed;
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"{ex.Message}\r\n\r\n{ex.StackTrace}", ex.GetType().FullName);
            }
        }


        private async void btn_Start_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                Mouse.SetCursor(Cursors.Wait);
                if (_signalrClient is not null)
                {
                    try { await _signalrClient.StopAsync(); } catch { }
                    _signalrClient.Dispose();
                    _signalrClient = null;
                }

                _signalrClient = new SignalrClient(new Uri(_mainWVM.ApiDomain), _mainWVM.BotId);
                _signalrClient.OnConnectionStateChange += _signalrClient_OnConnectionStateChange;
                _signalrClient.OnPushWorkCommand += _signalrClient_OnPushWorkCommand;
                _signalrClient.OnCancelWorkCommand += _signalrClient_OnCancelWorkCommand;
                _signalrClient.OnChangeBotConfigCommand += _signalrClient_OnChangeBotConfigCommand;
                _signalrClient.OnGetInfoChannelCommand += _signalrClient_OnGetInfoChannelCommand;
                _signalrClient.OnDeleteProfilesCommand += _signalrClient_OnDeleteProfilesCommand;
                await _signalrClient.StartAsync();
                _signalrClient_OnConnectionStateChange(SignalRConnectionState.Connected);
                _works.MaxRun = _mainWVM.ThreadCount;
                _timer_ping.Start();
                _mainWVM.IsWorking = true;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"{ex.Message}\r\n\r\n{ex.StackTrace}", ex.GetType().FullName);
            }
            finally
            {
                Mouse.SetCursor(null);
            }
        }

        private async void btn_Stop_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                Mouse.SetCursor(Cursors.Wait);
                _timer_ping.Stop();
                await _signalrClient?.StopAsync();
                _signalrClient?.Dispose();
                _signalrClient = null;
                _works.ShutDown();
                _mainWVM.IsWorking = false;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"{ex.Message}\r\n\r\n{ex.StackTrace}", ex.GetType().FullName);
            }
            finally
            {
                Mouse.SetCursor(null);
            }
        }


        private void lv_gridheader_Group_Click(object sender, RoutedEventArgs e)
        {
            _mainWVM.YoutubeChannels.SortGroup();
        }

        private void TextBlockEdit_MouseDown(object sender, MouseButtonEventArgs e)
        {
            if (sender is TextBlockEdit textBlockEdit)
            {
                textBlockEdit.IsEditing = true;
            }
        }

        private void lv_YoutubeChannels_MenuItem_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                Mouse.SetCursor(Cursors.Wait);
                MenuItem menuItem = sender as MenuItem;
                EnumVM<YoutubeChannelMenu> menuVM = menuItem.DataContext as EnumVM<YoutubeChannelMenu>;
                var selectedItems = lv_YoutubeChannels.SelectedItems.Cast<YoutubeChannelVM>().ToList();
                switch (menuVM?.Value)
                {
                    case YoutubeChannelMenu.AddProfile:
                        {
                            _mainWVM.YoutubeChannels.Add(new YoutubeChannelVM(new ProfileData()));
                            break;
                        }
                    case YoutubeChannelMenu.AddProfileExist:
                        {
                            foreach (var item in Directory.GetDirectories(Singleton.ProfilesDir))
                            {
                                DirectoryInfo directoryInfo = new DirectoryInfo(item);
                                if (!_mainWVM.YoutubeChannels.Any(x => x.Data.ProfileId.Equals(directoryInfo.Name)))
                                {
                                    _mainWVM.YoutubeChannels.Add(new YoutubeChannelVM(new ProfileData()
                                    {
                                        ProfileId = directoryInfo.Name
                                    }));
                                }
                            };
                            break;
                        }

                    case YoutubeChannelMenu.DeleteSelectedProfile:
                        {
                            if (selectedItems.Count > 0 &&
                                MessageBox.Show("Xóa profiles đã chọn?", "Xác nhận", MessageBoxButton.OKCancel, MessageBoxImage.Warning) == MessageBoxResult.OK)
                            {
                                foreach (var item in selectedItems.Where(x => x.InWorkCount == 0))
                                {
                                    _mainWVM.YoutubeChannels.Remove(item);
                                    try
                                    {
                                        MainWVM.WriteLog($"Deleting profile: {item.Data.ProfileId}");
                                        item.ChromeProfileVM.YoutubeProfile.CloseChrome();
                                        Directory.Delete(item.ChromeProfileVM.ProfileDir, true);
                                        MainWVM.WriteLog($"Deleted profile: {item.Data.ProfileId}");
                                    }
                                    catch (Exception ex)
                                    {
                                        MainWVM.WriteExceptionLog(ex);
                                    }
                                }
                            }
                            break;
                        }

                    case YoutubeChannelMenu.CheckYoutubeProfile:
                        {
                            var selectedItem = selectedItems.FirstOrDefault();
                            if (selectedItem is not null)
                            {
                                _works.Add(new GetInfoChannelWork(selectedItem));
                            }
                            break;
                        }

                    case YoutubeChannelMenu.OpenNonSelenium:
                        {
                            var selectedItem = selectedItems.FirstOrDefault(x => x.InWorkCount == 0);
                            selectedItem?.ChromeProfileVM.YoutubeProfile.OpenHand(string.Empty);
                            break;
                        }
                }
            }
            catch (Exception ex)
            {
                MainWVM.WriteExceptionLog(ex);
                MessageBox.Show($"{ex.Message}\r\n\r\n{ex.StackTrace}", ex.GetType().FullName);
            }
            finally
            {
                Mouse.SetCursor(null);
            }
        }


        private void YoutubeChannels_OnProfilesChanged()
        {
            _timer_updateChannel.Stop();
            _timer_updateChannel.Start();
        }
        private void Timer_updateChannel_Elapsed(object sender, ElapsedEventArgs e)
        {
            if (_signalrClient?.ServerHub is not null)
            {
                _signalrClient?.ServerHub?.ChromeProfileUpdateAsync(_mainWVM.YoutubeChannels.GetChromeProfileDatas().ToList());
            }
        }



        private void _signalrClient_OnConnectionStateChange(SignalRConnectionState obj)
        {
            MainWVM.WriteLog($"ConnectionState: {obj}");
            _mainWVM.ConnectionState = obj;
            if (obj == SignalRConnectionState.Connected)
            {
                _timer_updateChannel.Stop();
                _timer_updateChannel.Start();
                UpdateQueueIndex(true);
            }
        }

        private void _signalrClient_OnPushWorkCommand(WorkData obj)
        {
            if (obj is null) return;
            try
            {
                MainWVM.WriteLog($"[{obj.ItemId}-{obj.WorkId}] {obj.ScheduleTime}");

                YoutubeChannelVM youtubeChannelVM = _mainWVM.YoutubeChannels.FirstOrDefault(x => x.Data.ProfileId.Equals(obj.ProfileId));
                if (youtubeChannelVM is not null)
                {
                    AddQueueMainWork(new MainWork(youtubeChannelVM, obj, _signalrClient.ServerHub));
                }
                else
                {
                    _signalrClient?.ServerHub?.WorkUpdateAsync(new WorkResponse(obj.ItemId, obj.WorkId, WorkStatus.Error)
                    {
                        Message = $"Không tìm thấy profile '{obj.ProfileId}'",
                    });
                    MainWVM.WriteLog($"[{obj.ItemId}-{obj.WorkId}] Không tìm thấy profile");
                }
            }
            catch (Exception ex)
            {
                _signalrClient?.ServerHub?.WorkUpdateAsync(new WorkResponse(obj.ItemId, obj.WorkId, WorkStatus.Error)
                {
                    ExceptionInfo = new ExceptionInfo(ex)
                });
                MainWVM.WriteExceptionLog($"[{obj.ItemId}-{obj.WorkId}]", ex);
            }
        }

        private void _signalrClient_OnCancelWorkCommand(Identy identy)
        {
            if (identy is null) return;
            void __signalrClient_OnCancelWorkCommand()
            {
                try
                {
                    MainWVM.WriteLog($"[{identy.ItemId}-{identy.WorkId}] Cancel");
                    CancelQueueMainWork(identy);
                }
                catch (Exception ex)
                {
                    MainWVM.WriteExceptionLog(ex);
                }
            };

            //make same thread with _timer_schedule_Elapsed for not add to queue
            this.Dispatcher.InvokeAsync(__signalrClient_OnCancelWorkCommand);
        }

        private void _signalrClient_OnChangeBotConfigCommand(BotConfig botConfig)
        {
            if (botConfig is null) return;
            try
            {
                _mainWVM.ThreadCount = Math.Max(1, botConfig.ThreadCount);
                MainWVM.WriteLog($"{nameof(botConfig.ThreadCount)}: {botConfig.ThreadCount}");

            }
            catch (Exception ex)
            {
                MainWVM.WriteExceptionLog(ex);
            }
        }

        private void _signalrClient_OnGetInfoChannelCommand(string profileId)
        {
            if (string.IsNullOrWhiteSpace(profileId)) return;
            try
            {
                YoutubeChannelVM youtubeChannelVM = _mainWVM.YoutubeChannels.FirstOrDefault(x => profileId.Equals(x.Data.ProfileId));
                if (youtubeChannelVM is not null)
                {
                    if (_works.Add(new GetInfoChannelWork(youtubeChannelVM)))
                    {
                        MainWVM.WriteLog($"ProfileId: {profileId}, ChannelName: {youtubeChannelVM?.ChannelName}");
                    }
                    else
                    {
                        MainWVM.WriteLog($"ProfileId: {profileId} {nameof(GetInfoChannelWork)} đang được thực hiện");
                    }
                }
                else
                {
                    MainWVM.WriteLog($"ProfileId: {profileId} Không tìm thấy profile");
                }
            }
            catch (Exception ex)
            {
                MainWVM.WriteExceptionLog(ex);
            }
        }

        private async void _signalrClient_OnDeleteProfilesCommand(IReadOnlyList<string> profileIds)
        {
            if (profileIds is null) return;
            foreach (var item in _mainWVM.YoutubeChannels.ToList())
            {
                if (item.InWorkCount == 0 && profileIds.Contains(item.Data.ProfileId))
                {
                    try
                    {
                        MainWVM.WriteLog($"Deleting profile: {item.Data.ProfileId}");

                        await this.Dispatcher.InvokeAsync(() => _mainWVM.YoutubeChannels.Remove(item));
                        item.ChromeProfileVM.YoutubeProfile.CloseChrome();
                        await Task.Factory.StartNew(() => Directory.Delete(item.ChromeProfileVM.ProfileDir, true), TaskCreationOptions.LongRunning);

                        MainWVM.WriteLog($"Deleted profile: {item.Data.ProfileId}");
                    }
                    catch (Exception ex)
                    {
                        MainWVM.WriteExceptionLog(ex);
                    }
                }
            }
            YoutubeChannels_OnProfilesChanged();
        }



        private async void AddQueueMainWork(MainWork mainWork)
        {
            if (mainWork is null) return;
            try
            {
                if (mainWork.WorkData.ScheduleTime.HasValue && mainWork.WorkData.ScheduleTime.Value > DateTime.Now)
                {
                    if (await _scheduleServiceMainWork.AddAsync(mainWork, mainWork.WorkData.ScheduleTime.Value))
                    {
                        MainWVM.WriteLog($"[{mainWork.WorkData.ItemId}-{mainWork.WorkData.WorkId}] " +
                            $"Vào xếp lịch {mainWork.WorkData.ScheduleTime.Value:HH:mm:ss dd/MM/yyyy}");
                        Task task = _signalrClient?.ServerHub?.WorkUpdateAsync(new WorkResponse(mainWork.WorkData.ItemId, mainWork.WorkData.WorkId, WorkStatus.Schedule));
                        if (task is not null) await task;
                    }
                    else
                    {
                        MainWVM.WriteLog($"[{mainWork.WorkData.ItemId}-{mainWork.WorkData.WorkId}] Vào xếp lịch thất bại (trùng lặp)");
                        mainWork.Dispose();
                    }
                }
                else
                {
                    if (_works.Add(mainWork))
                    {
                        Task task = _signalrClient?.ServerHub?.WorkUpdateAsync(new WorkResponse(mainWork.WorkData.ItemId, mainWork.WorkData.WorkId, WorkStatus.Queueing));
                        if (task is not null) await task;
                        MainWVM.WriteLog($"[{mainWork.WorkData.ItemId}-{mainWork.WorkData.WorkId}] Vào hàng chờ");
                        UpdateQueueIndex();
                    }
                    else
                    {
                        MainWVM.WriteLog($"[{mainWork.WorkData.ItemId}-{mainWork.WorkData.WorkId}] Vào hàng chờ thất bại (trùng lặp)");
                        mainWork.Dispose();
                    }
                }
            }
            catch (Exception ex)
            {
                MainWVM.WriteExceptionLog(ex);
            }
        }
        private async void CancelQueueMainWork(Identy identy)
        {
            if (identy is null) return;
            try
            {
                IEnumerable<BaseWork> baseWorks = _works.Cancel(x => x is MainWork mainWork && mainWork.WorkData.ItemId.Equals(identy.ItemId));
                IEnumerable<MainWork> mainWorks = await _scheduleServiceMainWork.RemoveAsync(x => x.WorkData.ItemId.Equals(identy.ItemId));
                foreach (MainWork mainWork in baseWorks.Cast<MainWork>().Concat(mainWorks))
                {
                    MainWVM.WriteLog($"[{mainWork.WorkData.ItemId}-{mainWork.WorkData.WorkId}] Đã hủy hàng chờ/xếp lịch");
                    Task task = _signalrClient?.ServerHub?.WorkUpdateAsync(new WorkResponse(mainWork.WorkData.ItemId, mainWork.WorkData.WorkId, WorkStatus.Cancelled));
                    if (task is not null) await task;
                }
            }
            catch (Exception ex)
            {
                MainWVM.WriteExceptionLog(ex);
            }
        }

        private void UpdateQueueIndex(bool isUpdateSchedule = false)
        {
            async void _UpdateQueueIndex()
            {
                if (_signalrClient is null) return;
                try
                {
                    int index = 0;
                    foreach (MainWork item in _works.Queues.ToList().Where(x => x is MainWork).Cast<MainWork>())
                    {
                        WorkResponse workResponse = new WorkResponse(item.WorkData.ItemId, item.WorkData.WorkId, WorkStatus.Queueing);
                        workResponse.QueueIndex = index++;
                        Task task = _signalrClient?.ServerHub?.WorkUpdateAsync(workResponse);
                        if (task is not null) await task;
                    }
                    if (isUpdateSchedule)
                    {
                        foreach (MainWork item in _scheduleServiceMainWork.ScheduleList.ToList())
                        {
                            Task task = _signalrClient?.ServerHub?.WorkUpdateAsync(new WorkResponse(item.WorkData.ItemId, item.WorkData.WorkId, WorkStatus.Schedule));
                            if (task is not null) await task;
                        }
                    }
                }
                catch (Exception ex)
                {
                    MainWVM.WriteExceptionLog(ex);
                }
            }

            if (this.Dispatcher.CheckAccess())
            {
                _UpdateQueueIndex();
            }
            else
            {
                _ = this.Dispatcher.InvokeAsync(_UpdateQueueIndex);
            }
        }
    }
}
