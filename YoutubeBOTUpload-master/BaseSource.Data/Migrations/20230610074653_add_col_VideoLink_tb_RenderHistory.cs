using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BaseSource.Data.Migrations
{
    public partial class add_col_VideoLink_tb_RenderHistory : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "VideoLink",
                table: "RenderHistorys",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AlterColumn<DateTime>(
                name: "UpdatedTime",
                table: "ChannelYoutubes",
                type: "datetime2",
                nullable: true,
                oldClrType: typeof(DateTime),
                oldType: "datetime2");

            migrationBuilder.AddColumn<DateTime>(
                name: "DeletedTime",
                table: "ChannelYoutubes",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Gmail",
                table: "ChannelYoutubes",
                type: "nvarchar(255)",
                maxLength: 255,
                nullable: true);

            migrationBuilder.UpdateData(
                table: "AppRoles",
                keyColumn: "Id",
                keyValue: "c1105ce5-9dbc-49a9-a7d5-c963b6daa62a",
                column: "ConcurrencyStamp",
                value: "20ad3e6d-b42e-4468-b15c-8fbdd775c6f1");

            migrationBuilder.UpdateData(
                table: "AppUsers",
                keyColumn: "Id",
                keyValue: "ffded6b0-3769-4976-841b-69459049a62d",
                columns: new[] { "ConcurrencyStamp", "PasswordHash" },
                values: new object[] { "1ae141eb-9c0e-4b68-9876-ab8863226fa6", "AQAAAAEAACcQAAAAEBwG5oxalR1QQyL+GYIUzKw68NQnUcx/B9DS6MRjlSwKKn+e9GblXdN+873rxC2DvQ==" });
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "VideoLink",
                table: "RenderHistorys");

            migrationBuilder.DropColumn(
                name: "DeletedTime",
                table: "ChannelYoutubes");

            migrationBuilder.DropColumn(
                name: "Gmail",
                table: "ChannelYoutubes");

            migrationBuilder.AlterColumn<DateTime>(
                name: "UpdatedTime",
                table: "ChannelYoutubes",
                type: "datetime2",
                nullable: false,
                defaultValue: new DateTime(1, 1, 1, 0, 0, 0, 0, DateTimeKind.Unspecified),
                oldClrType: typeof(DateTime),
                oldType: "datetime2",
                oldNullable: true);

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
        }
    }
}
