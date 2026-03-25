using System;
using System.Collections;
using System.Collections.Generic;
using System.Collections.Specialized;
using System.ComponentModel;
using System.Linq;
using System.Reflection;
using System.Windows.Controls;
using System.Windows;
using TqkLibrary.WpfUi.ObservableCollection;
using UploadYoutubeBot.DataClass;
using GongSolutions.Wpf.DragDrop;
using GongSolutions.Wpf.DragDrop.Utilities;
using BaseSource.SharedSignalrData.Classes;

namespace UploadYoutubeBot.UI.ViewModels
{
    class YoutubeChannelVMSaveObservableCollection : SaveObservableCollection<ProfileData, YoutubeChannelVM>, IDropTarget
    {
        public event Action OnProfilesChanged;
        public YoutubeChannelVMSaveObservableCollection()
            : base(Singleton.ListYoutubeChannelPath, x => new YoutubeChannelVM(x))
        {
            this.CollectionChanged += UploadConfigureVMSaveObservableCollection_CollectionChanged;
            CalcIndex();

            foreach (var item in this)
            {
                item.ChromeProfileVM.Change += ChromeProfileVM_Change;
            }
        }

        private void UploadConfigureVMSaveObservableCollection_CollectionChanged(object sender, NotifyCollectionChangedEventArgs e)
        {
            if (e.NewItems is not null)
            {
                foreach (var item in e.NewItems.Cast<YoutubeChannelVM>())
                {
                    item.ChromeProfileVM.Change += ChromeProfileVM_Change;
                }
            }
            if (e.OldItems is not null)
            {
                foreach (var item in e.OldItems.Cast<YoutubeChannelVM>())
                {
                    item.ChromeProfileVM.Change -= ChromeProfileVM_Change;
                }
            }


            CalcIndex();
            OnProfilesChanged?.Invoke();
        }

        private void ChromeProfileVM_Change(object obj, ProfileData data)
        {
            OnProfilesChanged?.Invoke();
        }

        void CalcIndex()
        {
            int i = 1;
            foreach (var item in this) item.STT = i++;
        }

        bool isOrder = false;
        public void SortGroup()
        {
            List<YoutubeChannelVM> list = (isOrder ? this.OrderByDescending(x => x.GroupName) : this.OrderBy(x => x.GroupName)).ToList();
            isOrder = !isOrder;
            for (int i = 0; i < list.Count; i++)
            {
                this.Move(IndexOf(list[i]), i);
            }
        }

        public IEnumerable<ChromeProfileData> GetChromeProfileDatas()
        {
            foreach (var item in this.Where(x => !string.IsNullOrWhiteSpace(x.ChannelId)))
            {
                yield return new ChromeProfileData()
                {
                    AvatarUrl = item.Data.AvatarUrl,
                    ChannelId = item.Data.ChannelId,
                    ChannelName = item.Data.ChannelName,
                    Email = item.Data.Email,
                    ProfileId = item.Data.ProfileId,
                };
            }
        }

        #region IDropTarget

        public virtual void DragOver(IDropInfo dropInfo)
        {
            if (CanAcceptData(dropInfo))
            {
                dropInfo.Effects = DragDropEffects.Copy;
                dropInfo.DropTargetAdorner = DropTargetAdorners.Insert;
            }
        }

        public virtual void Drop(IDropInfo dropInfo)
        {
            YoutubeChannelVMSaveObservableCollection destination_List = dropInfo.TargetCollection as YoutubeChannelVMSaveObservableCollection;
            int insertIndex = dropInfo.InsertIndex;
            if (dropInfo.Data is DataObject dataObject)
            {

            }
            else
            {
                YoutubeChannelVMSaveObservableCollection source_List = dropInfo.DragInfo.SourceCollection as YoutubeChannelVMSaveObservableCollection;
                if (source_List != null)
                {
                    IEnumerable data = ExtractData(dropInfo.Data);

                    List<YoutubeChannelVM> datas = new List<YoutubeChannelVM>();
                    foreach (object o in data) datas.Add((YoutubeChannelVM)o);
                    datas = datas.OrderBy(x => source_List.IndexOf(x)).ToList();//sort as index

                    foreach (YoutubeChannelVM VideoFileVM in datas)
                    {
                        if (source_List == destination_List)//self -> self
                        {
                            int index_item = source_List.IndexOf(VideoFileVM);
                            source_List.Move(index_item, insertIndex > index_item ? insertIndex - 1 : insertIndex++);
                        }
                    }
                }
            }
        }

        protected static bool CanAcceptData(IDropInfo dropInfo)
        {
            if (dropInfo.Data is DataObject dataObject)
            {
                return false;
            }
            else if (dropInfo.DragInfo != null)
            {
                if (dropInfo.DragInfo.SourceCollection == dropInfo.TargetCollection)
                {
                    return GetList(dropInfo.TargetCollection) != null;
                }
                else if (dropInfo.DragInfo.SourceCollection is ItemCollection)
                {
                    return false;
                }
                else
                {
                    if (TestCompatibleTypes(dropInfo.TargetCollection, dropInfo.Data))
                    {
                        return !IsChildOf(dropInfo.VisualTargetItem, dropInfo.DragInfo.VisualSourceItem);
                    }
                }
            }
            return false;
        }

        protected static IEnumerable ExtractData(object data)
        {
            if (data is IEnumerable && !(data is string)) return (IEnumerable)data;
            else return Enumerable.Repeat(data, 1);
        }

        protected static IList GetList(IEnumerable enumerable)
        {
            if (enumerable is ICollectionView) return ((ICollectionView)enumerable).SourceCollection as IList;
            else return enumerable as IList;
        }

        protected static bool IsChildOf(UIElement targetItem, UIElement sourceItem)
        {
            ItemsControl parent = ItemsControl.ItemsControlFromItemContainer(targetItem);
            while (parent != null)
            {
                if (parent == sourceItem) return true;
                parent = ItemsControl.ItemsControlFromItemContainer(parent);
            }
            return false;
        }

        protected static bool TestCompatibleTypes(IEnumerable target, object data)
        {
            TypeFilter filter = (t, o) =>
            {
                return (t.IsGenericType && t.GetGenericTypeDefinition() == typeof(IEnumerable<>));
            };

            var enumerableInterfaces = target.GetType().FindInterfaces(filter, null);
            var enumerableTypes = from i in enumerableInterfaces select i.GetGenericArguments().Single();

            if (enumerableTypes.Count() > 0)
            {
                Type dataType = TypeUtilities.GetCommonBaseClass(ExtractData(data));
                return enumerableTypes.Any(t => t.IsAssignableFrom(dataType));
            }
            else
            {
                return target is IList;
            }
        }

        #endregion IDropTarget

    }
}
