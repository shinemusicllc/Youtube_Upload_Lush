using BaseSource.SharedSignalrData.Classes;
using BaseSource.SharedSignalrData.Interfaces;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TqkLibrary.Queues.TaskQueues;
using UploadYoutubeBot.UI.ViewModels;
using FFmpegArgs.Executes;
using FFMpegCore;
using System.IO;
using BaseSource.SharedSignalrData.Enums;
using Xceed.Wpf.Toolkit.PropertyGrid.Attributes;
using System.Text.RegularExpressions;

namespace UploadYoutubeBot.Works
{
    internal partial class MainWork
    {
        DateTime? _TimeStartRender = null;
        protected async Task<string> RenderAsync()
        {
            //check
            if (!WorkData.FileDatas.Any(x => x.FilePosition == FilePosition.Loop && x.FileType == FileType.Video))
            {
                throw new Exception($"Không có video loop");
            }
            //TH1: Video loop, Audio loop
            //TH2: Video intro, Video loop, Audio loop
            //TH3: Video loop, Audio loop, Audio Outro
            //TH4: Video intro, Video loop, Audio loop, Audio Outro


            //MediaAnalysis
            Dictionary<FileData, IMediaAnalysis> dict_FileData_MediaAnalysis = new Dictionary<FileData, IMediaAnalysis>();
            foreach (var item in WorkData.FileDatas)
            {
                string filePath = Path.Combine(WorkingDir, item.Name);
                dict_FileData_MediaAnalysis[item] = await FFProbe.AnalyseAsync(filePath, cancellationToken: CancellationToken);
            }

            //check MediaAnalysis
            foreach (var item in WorkData.FileDatas.Where(x => x.FileType == FileType.Audio))
            {
                if (dict_FileData_MediaAnalysis[item].PrimaryAudioStream is null)
                {
                    throw new Exception($"file {item.Name} không có âm thanh");
                }
            }
            bool isHaveAudioLoopFile = WorkData.FileDatas.Any(x => x.FileType == FileType.Audio && x.FilePosition == FilePosition.Loop);
            foreach (var item in WorkData.FileDatas.Where(x => x.FileType == FileType.Video))
            {
                if (dict_FileData_MediaAnalysis[item].PrimaryVideoStream is null)
                {
                    throw new Exception($"file {item.Name} không có hình ảnh");
                }
                if (!isHaveAudioLoopFile && dict_FileData_MediaAnalysis[item].PrimaryAudioStream is null)
                {
                    throw new Exception($"file {item.Name} không có âm thanh");
                }
                if (dict_FileData_MediaAnalysis[item].PrimaryVideoStream.FrameRate != Math.Round(dict_FileData_MediaAnalysis[item].PrimaryVideoStream.FrameRate, 0))
                {
                    throw new Exception($"file {item.Name} fps không phải số nguyên ({dict_FileData_MediaAnalysis[item].PrimaryVideoStream.FrameRate})");
                }
            }
            if (WorkData.FileDatas.Where(x => x.FileType == FileType.Video).GroupBy(x => dict_FileData_MediaAnalysis[x].PrimaryVideoStream.Width).Count() > 1 ||
                WorkData.FileDatas.Where(x => x.FileType == FileType.Video).GroupBy(x => dict_FileData_MediaAnalysis[x].PrimaryVideoStream.Height).Count() > 1)
            {
                throw new Exception($"Các video có kích thước khung hình không khớp");
            }

            List<RenderInfo> renderInfos = new List<RenderInfo>();

            //convert all to ts
            foreach (var item in WorkData.FileDatas.Where(x => x.FileType == FileType.Video))
            {
                string newName = item.Name.Substring(0, item.Name.Length - ".mp4".Length) + ".ts";
                renderInfos.Add(new RenderInfo()
                {
                    Argument = $"-y -i {item.Name} -c copy {newName}"
                });
                item.Name = newName;
            }

            //video
            List<string> videoFiles = new List<string>();
            {
                TimeSpan duration = TimeSpan.Zero;
                var videoIntroFileData = WorkData.FileDatas.FirstOrDefault(x => x.FileType == FileType.Video && x.FilePosition == FilePosition.Intro);
                if (videoIntroFileData is not null)
                {
                    if (WorkData.DurationOutput <= dict_FileData_MediaAnalysis[videoIntroFileData].Duration)
                        throw new Exception($"Video intro dài hơn đầu ra");

                    videoFiles.Add(videoIntroFileData.Name);
                    duration += dict_FileData_MediaAnalysis[videoIntroFileData].Duration;
                }

                var videoOutroFileData = WorkData.FileDatas.FirstOrDefault(x => x.FileType == FileType.Video && x.FilePosition == FilePosition.Outro);
                if (videoOutroFileData is not null)
                {
                    duration += dict_FileData_MediaAnalysis[videoOutroFileData].Duration;
                }

                var videoLoopFileDatas = WorkData.FileDatas.Where(x => x.FileType == FileType.Video && x.FilePosition == FilePosition.Loop).ToList();
                int index = 0;
                while (duration < WorkData.DurationOutput)
                {
                    var videoLoopFileData = videoLoopFileDatas[index % videoLoopFileDatas.Count];
                    IMediaAnalysis mediaAnalysis = dict_FileData_MediaAnalysis[videoLoopFileData];
                    if (mediaAnalysis.Duration + duration < WorkData.DurationOutput)
                    {
                        duration += mediaAnalysis.Duration;
                        videoFiles.Add(videoLoopFileData.Name);
                    }
                    else
                    {
                        //cut
                        TimeSpan cut_duration = WorkData.DurationOutput - duration;
                        renderInfos.Add(new RenderInfo()
                        {
                            Argument = $"-y -i \"{videoLoopFileData.Name}\" -c copy -t {cut_duration.TotalSeconds} cut.ts",
                            Time = cut_duration,
                        });
                        duration += cut_duration;
                        videoFiles.Add("cut.ts");
                    }
                    index++;
                }

                if (videoOutroFileData is not null)
                {
                    videoFiles.Add(videoOutroFileData.Name);
                }
            }

            //Audio
            List<string> audioFiles = new List<string>();
            if (isHaveAudioLoopFile)
            {
                TimeSpan duration = TimeSpan.Zero;
                var audioIntroFileData = WorkData.FileDatas.FirstOrDefault(x => x.FileType == FileType.Audio && x.FilePosition == FilePosition.Intro);
                if (audioIntroFileData is not null)
                {
                    if (WorkData.DurationOutput <= dict_FileData_MediaAnalysis[audioIntroFileData].Duration)
                        throw new Exception($"Audio intro dài hơn đầu ra");

                    audioFiles.Add(audioIntroFileData.Name);
                    duration += dict_FileData_MediaAnalysis[audioIntroFileData].Duration;
                }

                var audioOutroFileData = WorkData.FileDatas.FirstOrDefault(x => x.FileType == FileType.Audio && x.FilePosition == FilePosition.Outro);
                if (audioOutroFileData is not null)
                {
                    duration += dict_FileData_MediaAnalysis[audioOutroFileData].Duration;
                }

                var audioLoopFileDatas = WorkData.FileDatas.Where(x => x.FileType == FileType.Audio && x.FilePosition == FilePosition.Loop).ToList();
                int index = 0;
                while (duration < WorkData.DurationOutput)
                {
                    var audioLoopFileData = audioLoopFileDatas[index % audioLoopFileDatas.Count];
                    IMediaAnalysis mediaAnalysis = dict_FileData_MediaAnalysis[audioLoopFileData];
                    if (mediaAnalysis.Duration + duration < WorkData.DurationOutput)
                    {
                        duration += mediaAnalysis.Duration;
                        audioFiles.Add(audioLoopFileData.Name);
                    }
                    else
                    {
                        //cut
                        TimeSpan cut_duration = WorkData.DurationOutput - duration;
                        renderInfos.Add(new RenderInfo()
                        {
                            Argument = $"-y -i \"{audioLoopFileData.Name}\" -c copy -t {cut_duration.TotalSeconds} cut.mp3",
                            Time = cut_duration,
                        });
                        duration += cut_duration;
                        audioFiles.Add("cut.mp3");
                    }
                    index++;
                }

                if (audioOutroFileData is not null)
                {
                    audioFiles.Add(audioOutroFileData.Name);
                }
            }


            string videoTxtPath = Path.Combine(WorkingDir, "videos.txt");
            File.WriteAllText(videoTxtPath, string.Join("\r\n", videoFiles.Select(x => $"file '{x}'")), Encoding.ASCII);

            string audioConcatProtocol = isHaveAudioLoopFile ? "concat:" + string.Join("|", audioFiles) : string.Empty;
            string fileOutput = string.IsNullOrWhiteSpace(WorkData.UploadTitleName) ? "out.mp4" : $"{WorkData.UploadTitleName}.mp4";

            {
                List<string> arguments = new List<string>();
                arguments.Add("-y");
                if (isHaveAudioLoopFile) arguments.Add("-an");
                arguments.Add("-f concat -safe 0 -i videos.txt");
                if (isHaveAudioLoopFile)
                {
                    arguments.Add($"-vn -i \"{audioConcatProtocol}\"");
                }
                //arguments.Add("-movflags +faststart");
                arguments.Add("-c copy");
                arguments.Add($"-t {WorkData.DurationOutput.TotalSeconds}");
                arguments.Add($"\"{fileOutput}\"");

                renderInfos.Add(new RenderInfo()
                {
                    Argument = string.Join(" ", arguments),
                    Time = WorkData.DurationOutput,
                });
            }

            _TimeStartRender = DateTime.Now;

            using StreamWriter streamWriter_renderLog = new StreamWriter(Path.Combine(Singleton.LogDir, $"{DateTime.Now:yyyy-MM-dd} {WorkData.ItemId}-{WorkData.WorkId}.log"));
            for (int i = 0; i < renderInfos.Count; i++)
            {
                FFmpegRender ffmpegRender = FFmpegRender.FromArguments(renderInfos[i].Argument, new FFmpegRenderConfig()
                {
                    WorkingDirectory = WorkingDir,
                    FFmpegBinaryPath = Singleton.FFmpeg
                });
                ffmpegRender.OnEncodingProgress += async (RenderProgress obj) =>
                {
                    await UpdateRenderAsync(obj, i + 1, renderInfos.Count, renderInfos[i].Time);
                };
                var result = await ffmpegRender.ExecuteAsync(CancellationToken);

                streamWriter_renderLog.WriteLine($"Argument: {renderInfos[i].Argument}");
                streamWriter_renderLog.WriteLine($"ExitCode: {result.ExitCode}");
                streamWriter_renderLog.WriteLine($"OutputData:");
                foreach (var line in result.ErrorDatas) streamWriter_renderLog.WriteLine(line);
                streamWriter_renderLog.WriteLine();
                streamWriter_renderLog.WriteLine();

                CancellationToken.ThrowIfCancellationRequested();
                result.EnsureSuccess();
            }

            return Path.Combine(WorkingDir, fileOutput);
        }

        class RenderInfo
        {
            public string Argument { get; init; }
            public TimeSpan Time { get; init; }
        }
    }
}