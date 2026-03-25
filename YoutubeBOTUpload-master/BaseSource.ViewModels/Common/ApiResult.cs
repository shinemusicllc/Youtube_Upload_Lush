using Microsoft.AspNetCore.Mvc.ModelBinding;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.ViewModels.Common
{
    public class ApiResult<T>
    {
        public bool IsSuccessed { get; set; }

        public string Message { get; set; }

        public T ResultObj { get; set; }

        public List<JsonModelValidation> ValidationErrors { get; set; }
    }

    public class ApiSuccessResult<T> : ApiResult<T>
    {
        public ApiSuccessResult(T resultObj, string message = null)
        {
            IsSuccessed = true;
            ResultObj = resultObj;
            Message = message;
        }

        public ApiSuccessResult()
        {
            IsSuccessed = true;
        }
    }
    public class ApiErrorResult<T> : ApiResult<T>
    {
        public ApiErrorResult()
        {
        }

        public ApiErrorResult(string message)
        {
            IsSuccessed = false;
            Message = message;
        }

        public ApiErrorResult(List<JsonModelValidation> validationErrors)
        {
            IsSuccessed = false;
            ValidationErrors = new List<JsonModelValidation>(validationErrors);
        }
    }

    public class JsonModelValidation
    {
        public string Pos { get; set; }
        public string Error { get; set; }
    }

    public static class ModelStateExtensions
    {
        public static void AddListErrors(this ModelStateDictionary ModelState, List<JsonModelValidation> validationErrors)
        {
            if (validationErrors != null)
            {
                foreach (var item in validationErrors)
                {
                    ModelState.AddModelError(item.Pos, item.Error);
                }
            }
        }

        public static List<JsonModelValidation> GetListErrors(this ModelStateDictionary ModelState)
        {
            var errors = new List<JsonModelValidation>();

            foreach (var vl in ModelState)
            {
                if (vl.Value.Errors.Count > 0)
                {
                    var er = new JsonModelValidation();
                    er.Pos = vl.Key;
                    foreach (var err in vl.Value.Errors)
                    {
                        er.Error = err.ErrorMessage;
                        errors.Add(er);
                        break;
                    }
                }
            }

            return errors;
        }
    }
}
