using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Media;
using TqkLibrary.WpfUi;
using UploadYoutubeBot.Attributes;

namespace UploadYoutubeBot.UI.ViewModels
{
    internal class EnumVM<T> where T : Enum
    {
        public EnumVM(T t)
        {
            this.Value = t;
            this.Text = t.GetAttribute<NameAttribute>()?.Name ?? t.ToString();
        }
        public EnumVM(T t, IEnumerable<EnumVM<T>> childs) : this(t)
        {
            Childs = childs?.ToList() ?? throw new ArgumentNullException(nameof(childs));
        }

        public string Text { get; }

        public T Value { get; }

        public ImageSource ImageSource { get; }

        public IEnumerable<EnumVM<T>> Childs { get; }
    }
}
