using Nito.AsyncEx;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using TqkLibrary.Queues.TaskQueues;
using UploadYoutubeBot.UI.ViewModels;

namespace UploadYoutubeBot.Services
{
    internal class ScheduleService<T> : IDisposable
    {
        readonly Dictionary<T, DateTime> _keyValuePairs = new Dictionary<T, DateTime>();
        readonly Action<T> _tillTheTime;
        public IEnumerable<T> ScheduleList { get { return _keyValuePairs.Keys; } }
        public ScheduleService(Action<T> tillTheTime)
        {
            this._tillTheTime = tillTheTime ?? throw new ArgumentNullException(nameof(tillTheTime));

            Task.Factory.StartNew(
                () => AsyncContext.Run(_scheduleLoop),
                TaskCreationOptions.LongRunning
                );
        }
        ~ScheduleService()
        {
            _isDisposed = true;
        }
        public void Dispose()
        {
            _isDisposed = true;
            GC.SuppressFinalize(this);
        }


        SynchronizationContext _synchronizationContext;
        bool _isDisposed = false;

        async void _scheduleLoop()
        {
            _synchronizationContext = SynchronizationContext.Current;
            while (!_isDisposed)
            {
                if (_keyValuePairs.Count > 0)
                {
                    var currTime = DateTime.Now;
                    foreach (var item in _keyValuePairs.Where(x => x.Value < currTime).ToList())
                    {
                        _keyValuePairs.Remove(item.Key);
                        try
                        {
                            _tillTheTime.Invoke(item.Key);
                        }
                        catch
                        {

                        }
                    }
                }
                await Task.Delay(100);
            }
        }



        public async Task<bool> AddAsync(T t, DateTime dateTime, CancellationToken cancellationToken = default)
        {
            if (_synchronizationContext is null) return false;

            return await _synchronizationContext.PostAsync<bool>(() =>
            {
                if (!this._keyValuePairs.ContainsKey(t))
                {
                    this._keyValuePairs.Add(t, dateTime);
                    return true;
                }
                return false;
            });
        }

        public async Task<bool> RemoveAsync(T t, CancellationToken cancellationToken = default)
        {
            if (_synchronizationContext is null) return false;

            return await _synchronizationContext.PostAsync<bool>(() => this._keyValuePairs.Remove(t));
        }
        public async Task<IReadOnlyList<T>> RemoveAsync(Func<T, bool> func, CancellationToken cancellationToken = default)
        {
            List<T> result = new List<T>();
            if (_synchronizationContext is not null)
            {
                await _synchronizationContext.PostAsync(() =>
                {
                    foreach (var pair in this._keyValuePairs.ToList())
                    {
                        if (func(pair.Key))
                        {
                            this._keyValuePairs.Remove(pair.Key);
                            result.Add(pair.Key);
                        }
                    }
                });
            }
            return result;
        }
    }
}
