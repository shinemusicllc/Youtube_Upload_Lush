using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace UploadYoutubeBot.UI
{
    /// <summary>
    /// Interaction logic for SearchUC.xaml
    /// </summary>
    public partial class SearchUC : UserControl
    {
        public SearchUC()
        {
            InitializeComponent();
        }

        public event Action<string> SearchTextChange;
        private void TB_SearchRender_TextChanged(object sender, TextChangedEventArgs e)
        {
            SearchTextChange?.Invoke(TB_SearchRender.Text);
        }

        private void btn_Clear_Click(object sender, RoutedEventArgs e)
        {
            TB_SearchRender.Text = string.Empty;
        }
    }
}
