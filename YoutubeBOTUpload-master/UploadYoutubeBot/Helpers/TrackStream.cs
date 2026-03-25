using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;

namespace UploadYoutubeBot.Helpers
{
    internal class TrackStream : Stream
    {
        readonly Stream _baseStream;
        readonly Action<int> _bufferTransferCallback;
        public TrackStream(Stream baseStream, Action<int> bufferTransferCallback)
        {
            _baseStream = baseStream ?? throw new ArgumentNullException(nameof(baseStream));
            _bufferTransferCallback = bufferTransferCallback ?? throw new ArgumentNullException(nameof(bufferTransferCallback));
        }
        protected override void Dispose(bool disposing)
        {
            base.Dispose(disposing);
        }

        public override bool CanRead => _baseStream.CanRead;

        public override bool CanSeek => _baseStream.CanSeek;

        public override bool CanWrite => _baseStream.CanWrite;

        public override long Length => _baseStream.Length;

        public override long Position { get => _baseStream.Position; set => _baseStream.Position = value; }

        public override void Flush()
        {
            _baseStream.Flush();
        }

        public override int Read(byte[] buffer, int offset, int count)
        {
            int result = _baseStream.Read(buffer, offset, count);
            _bufferTransferCallback.Invoke(result);
            return result;
        }

        public override long Seek(long offset, SeekOrigin origin)
        {
            return _baseStream.Seek(offset, origin);
        }

        public override void SetLength(long value)
        {
            _baseStream.SetLength(value);
        }

        public override void Write(byte[] buffer, int offset, int count)
        {
            _baseStream.Write(buffer, offset, count);
            _bufferTransferCallback.Invoke(count);
        }




        //https://devblogs.microsoft.com/pfxteam/overriding-stream-asynchrony/
        //must overwite BeginRead/EndRead, BeginWrite/EndWrite for asynchronous 
        public override IAsyncResult BeginRead(byte[] buffer, int offset, int count, AsyncCallback callback, object state)
        {
            return _baseStream.BeginRead(buffer, offset, count, callback, state);
        }
        public override IAsyncResult BeginWrite(byte[] buffer, int offset, int count, AsyncCallback callback, object state)
        {
            _bufferTransferCallback.Invoke(count);
            return _baseStream.BeginWrite(buffer, offset, count, callback, state);
        }
        public override int EndRead(IAsyncResult asyncResult)
        {
            int result = _baseStream.EndRead(asyncResult);
            _bufferTransferCallback.Invoke(result);
            return result;
        }
        public override void EndWrite(IAsyncResult asyncResult)
        {
            _baseStream.EndWrite(asyncResult);
        }

        public override async Task<int> ReadAsync(byte[] buffer, int offset, int count, CancellationToken cancellationToken = default)
        {
            int byte_read = await _baseStream.ReadAsync(buffer, offset, count, cancellationToken).ConfigureAwait(false);
            _bufferTransferCallback.Invoke(byte_read);
            return byte_read;
        }
        public override Task WriteAsync(byte[] buffer, int offset, int count, CancellationToken cancellationToken = default)
        {
            _bufferTransferCallback.Invoke(count);
            return _baseStream.WriteAsync(buffer, offset, count, cancellationToken);
        }
        public override Task FlushAsync(CancellationToken cancellationToken = default)
        {
            return _baseStream.FlushAsync(cancellationToken);
        }
#if NET5_0_OR_GREATER
        public override async ValueTask<int> ReadAsync(Memory<byte> buffer, CancellationToken cancellationToken = default)
        {
            int byte_read = await _baseStream.ReadAsync(buffer, cancellationToken);
            ThreadPool.QueueUserWorkItem((o) => _bufferTransferCallback.Invoke(byte_read));
            return byte_read;
        }
        public override ValueTask WriteAsync(ReadOnlyMemory<byte> buffer, CancellationToken cancellationToken = default)
        {
            ThreadPool.QueueUserWorkItem((o) => _bufferTransferCallback.Invoke(buffer.Length));
            return _baseStream.WriteAsync(buffer, cancellationToken);
        }
#endif
    }
}
