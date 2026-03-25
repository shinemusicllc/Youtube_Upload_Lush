using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using TqkLibrary.Queues.TaskQueues;
using UploadYoutubeBot.UI.ViewModels;

namespace UploadYoutubeBot.Works
{
    internal abstract class BaseWork : IWork
    {
        readonly CancellationTokenSource _cancellationTokenSource = new CancellationTokenSource();
        protected CancellationToken CancellationToken { get { return _cancellationTokenSource.Token; } }

        public YoutubeChannelVM YoutubeChannel { get; }
        protected BaseWork(
            YoutubeChannelVM youtubeChannelVM
            )
        {
            this.YoutubeChannel = youtubeChannelVM ?? throw new ArgumentNullException(nameof(youtubeChannelVM));
            this.YoutubeChannel.AddCount();
        }

        public virtual bool IsPrioritize => false;

        public void Cancel()
        {
            _cancellationTokenSource.Cancel();
        }

        public void Dispose()
        {
            _cancellationTokenSource.Dispose();
            this.YoutubeChannel.SubtractCount();
        }

        public abstract Task DoWork();
    }
}
