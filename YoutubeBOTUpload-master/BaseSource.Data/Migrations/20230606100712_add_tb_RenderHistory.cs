using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BaseSource.Data.Migrations
{
    public partial class add_tb_RenderHistory : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "ManagerBOTs",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    BotId = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: true),
                    ConnectionId = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: true),
                    Name = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: true),
                    Group = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: true),
                    Status = table.Column<byte>(type: "tinyint", nullable: false),
                    CreatedTime = table.Column<DateTime>(type: "datetime2", nullable: false),
                    DeletedTime = table.Column<DateTime>(type: "datetime2", nullable: true),
                    Retry = table.Column<int>(type: "int", nullable: false),
                    NumberOfThreads = table.Column<int>(type: "int", nullable: false),
                    CPU = table.Column<double>(type: "float", nullable: false),
                    RAM = table.Column<double>(type: "float", nullable: false),
                    Bandwidth = table.Column<double>(type: "float", nullable: false),
                    UpdatedTime = table.Column<DateTime>(type: "datetime2", nullable: true),
                    LiveType = table.Column<byte>(type: "tinyint", nullable: true),
                    IsUsed = table.Column<bool>(type: "bit", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ManagerBOTs", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "ChannelYoutubes",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    Name = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: true),
                    Avatar = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: true),
                    ChannelYTId = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: true),
                    ManagerBOTId = table.Column<int>(type: "int", nullable: false),
                    Cookie = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UpdatedTime = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CreatedTime = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ChannelYoutubes", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ChannelYoutubes_ManagerBOTs_ManagerBOTId",
                        column: x => x.ManagerBOTId,
                        principalTable: "ManagerBOTs",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "RenderHistorys",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    Order = table.Column<int>(type: "int", nullable: false),
                    UserId = table.Column<string>(type: "nvarchar(128)", nullable: true),
                    ChannelYoutubeId = table.Column<int>(type: "int", nullable: false),
                    Intro = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: true),
                    VideoLoop = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: true),
                    AudioLoop = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: true),
                    Outtro = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: true),
                    TimeRender = table.Column<TimeSpan>(type: "time", nullable: false),
                    VideoName = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: true),
                    CreatedTime = table.Column<DateTime>(type: "datetime2", nullable: false),
                    DeletedTime = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedTime = table.Column<DateTime>(type: "datetime2", nullable: true),
                    Status = table.Column<int>(type: "int", nullable: false),
                    Action = table.Column<int>(type: "int", nullable: false),
                    IsError = table.Column<bool>(type: "bit", nullable: false),
                    Pencent = table.Column<double>(type: "float", nullable: false),
                    ErrorMessage = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_RenderHistorys", x => x.Id);
                    table.ForeignKey(
                        name: "FK_RenderHistorys_AppUsers_UserId",
                        column: x => x.UserId,
                        principalTable: "AppUsers",
                        principalColumn: "Id");
                    table.ForeignKey(
                        name: "FK_RenderHistorys_ChannelYoutubes_ChannelYoutubeId",
                        column: x => x.ChannelYoutubeId,
                        principalTable: "ChannelYoutubes",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "UserChannels",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ChannelYoutubeId = table.Column<int>(type: "int", nullable: false),
                    UserId = table.Column<string>(type: "nvarchar(128)", nullable: true),
                    Status = table.Column<byte>(type: "tinyint", nullable: false),
                    CreatedTime = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_UserChannels", x => x.Id);
                    table.ForeignKey(
                        name: "FK_UserChannels_AppUsers_UserId",
                        column: x => x.UserId,
                        principalTable: "AppUsers",
                        principalColumn: "Id");
                    table.ForeignKey(
                        name: "FK_UserChannels_ChannelYoutubes_ChannelYoutubeId",
                        column: x => x.ChannelYoutubeId,
                        principalTable: "ChannelYoutubes",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.UpdateData(
                table: "AppRoles",
                keyColumn: "Id",
                keyValue: "c1105ce5-9dbc-49a9-a7d5-c963b6daa62a",
                column: "ConcurrencyStamp",
                value: "24a430fb-bf84-4ffc-81f6-156d02fa4d99");

            migrationBuilder.UpdateData(
                table: "AppUsers",
                keyColumn: "Id",
                keyValue: "ffded6b0-3769-4976-841b-69459049a62d",
                columns: new[] { "ConcurrencyStamp", "PasswordHash" },
                values: new object[] { "c8cf7700-8a36-4c86-b99b-9dd1810262d3", "AQAAAAEAACcQAAAAEDrhCZtx4ChN1xBCdQqcMrjUPwi6b20VB9RY7LDDGoTULaP+/gWqS4tyOcc/NWo7fg==" });

            migrationBuilder.CreateIndex(
                name: "IX_ChannelYoutubes_ManagerBOTId",
                table: "ChannelYoutubes",
                column: "ManagerBOTId");

            migrationBuilder.CreateIndex(
                name: "IX_RenderHistorys_ChannelYoutubeId",
                table: "RenderHistorys",
                column: "ChannelYoutubeId");

            migrationBuilder.CreateIndex(
                name: "IX_RenderHistorys_UserId",
                table: "RenderHistorys",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_UserChannels_ChannelYoutubeId",
                table: "UserChannels",
                column: "ChannelYoutubeId");

            migrationBuilder.CreateIndex(
                name: "IX_UserChannels_UserId",
                table: "UserChannels",
                column: "UserId");
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "RenderHistorys");

            migrationBuilder.DropTable(
                name: "UserChannels");

            migrationBuilder.DropTable(
                name: "ChannelYoutubes");

            migrationBuilder.DropTable(
                name: "ManagerBOTs");

            migrationBuilder.UpdateData(
                table: "AppRoles",
                keyColumn: "Id",
                keyValue: "c1105ce5-9dbc-49a9-a7d5-c963b6daa62a",
                column: "ConcurrencyStamp",
                value: "4b585131-e2e5-491a-8c14-999e2c6e0ee0");

            migrationBuilder.UpdateData(
                table: "AppUsers",
                keyColumn: "Id",
                keyValue: "ffded6b0-3769-4976-841b-69459049a62d",
                columns: new[] { "ConcurrencyStamp", "PasswordHash" },
                values: new object[] { "57d0094f-2825-4468-9b7b-28bdd3260e34", "AQAAAAEAACcQAAAAEMlrFbHdzE8peoj+33qHv96LloDOKSi6kDg1ZnbUDMNyIJGDnZMyEcGsO8iJpJhbKA==" });
        }
    }
}
