using System;
using System.Windows;
using System.Windows.Input;

namespace UploadYoutubeBot.UI.ViewModels
{
    internal class CopyCommand : ICommand
    {
        public event EventHandler CanExecuteChanged;

        public bool CanExecute(object parameter)
        {
            return true;
        }

        public void Execute(object parameter)
        {
            if (parameter is string str && !string.IsNullOrWhiteSpace(str))
            {
                Clipboard.SetText(str);
            }
        }
    }
}
