using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.ViewModels.Common
{
    public class PagedResult<T> : PagedResultBase
    {
        public List<T> Items { set; get; }
    }

    public class PagedResultBase
    {
        /// <summary>
        /// Gets or sets the index of the page.
        /// </summary>
        /// <value>The index of the page.</value>
        public int PageIndex { get; set; }
        /// <summary>
        /// Gets or sets the size of the page.
        /// </summary>
        /// <value>The size of the page.</value>
        public int PageSize { get; set; }
        /// <summary>
        /// Gets or sets the total count.
        /// </summary>
        /// <value>The total count.</value>
        public int TotalCount { get; set; }
        /// <summary>
        /// Gets or sets the total pages.
        /// </summary>
        /// <value>The total pages.</value>
        public int TotalPages { get; set; }
        /// <summary>
        /// Gets or sets the index from.
        /// </summary>
        /// <value>The index from.</value>
        public int IndexFrom { get; set; }

        /// <summary>
        /// Gets the has previous page.
        /// </summary>
        /// <value>The has previous page.</value>
        public bool HasPreviousPage => PageIndex - IndexFrom > 0;

        /// <summary>
        /// Gets the has next page.
        /// </summary>
        /// <value>The has next page.</value>
        public bool HasNextPage => PageIndex - IndexFrom + 1 < TotalPages;

        /// <summary>
        /// Gets the has page jump.
        /// </summary>
        /// <value>The has page jump</value>
        public int PageJump { get; set; }
        /// <summary>
        /// Gets the has start page
        /// </summary>
        /// <value>The has start page</value>
        public int StartPage { get; set; }
        /// <summary>
        /// Gets the has fish page
        /// </summary>
        /// <value>The has finish page</value>
        public int FinishPage { get; set; }
        public string PageUrl { get; set; }
    }

    public class PageQuery
    {

        private int _page;
        public int Page
        {
            get
            {
                return _page;
            }
            set
            {
                _page = value >= 1 ? value : 1;
            }
        }

        private int _pageSize;
        public int PageSize
        {
            get
            {
                return _pageSize;
            }
            set
            {
                switch (value)
                {
                    case 2:
                    case 5:
                    case 6:
                    case 8:
                    case 12:
                    case 15:
                    case 20:
                    case 30:
                    case 40:
                    case 50:
                    case 100:
                    case 200:
                    case 500:
                    case 800:
                    case 1000:
                    case 1500:
                    case 2000:
                    case 2500:
                    case 5000:
                    case 10000:
                        _pageSize = value;
                        break;

                    default:
                        _pageSize = 10;
                        break;
                }
            }
        }
    }
}
