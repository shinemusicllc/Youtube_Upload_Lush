using System.Text.Json.Serialization;
using System.Text.Json;

namespace BaseSource.SharedSignalrData
{
    public static class Extensions
    {
        public static JsonSerializerOptions SignalR_JsonSerializerOptions(this JsonSerializerOptions jsonSerializerOptions)
        {
            jsonSerializerOptions.NumberHandling = JsonNumberHandling.AllowNamedFloatingPointLiterals;
            jsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
            return jsonSerializerOptions;
        }
    }
}
