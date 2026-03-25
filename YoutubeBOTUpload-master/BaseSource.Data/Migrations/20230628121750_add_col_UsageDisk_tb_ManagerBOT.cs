using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BaseSource.Data.Migrations
{
    public partial class add_col_UsageDisk_tb_ManagerBOT : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<double>(
                name: "SpaceDisk",
                table: "ManagerBOTs",
                type: "float",
                nullable: false,
                defaultValue: 0.0);

            migrationBuilder.AddColumn<double>(
                name: "UsageDisk",
                table: "ManagerBOTs",
                type: "float",
                nullable: false,
                defaultValue: 0.0);

            migrationBuilder.UpdateData(
                table: "AppRoles",
                keyColumn: "Id",
                keyValue: "c1105ce5-9dbc-49a9-a7d5-c963b6daa62a",
                column: "ConcurrencyStamp",
                value: "ee4c6877-6174-41ec-bc23-088b48bc3f8b");

            migrationBuilder.UpdateData(
                table: "AppUsers",
                keyColumn: "Id",
                keyValue: "ffded6b0-3769-4976-841b-69459049a62d",
                columns: new[] { "ConcurrencyStamp", "PasswordHash" },
                values: new object[] { "e935e3b7-7c97-4a2d-978a-dff7be954b02", "AQAAAAEAACcQAAAAEB2T5FMir4QFoC+831U4BACA3HQfNpN73SsTjZTkV2IoT16vO0t8xWxlPV1r2Dy/qw==" });
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "SpaceDisk",
                table: "ManagerBOTs");

            migrationBuilder.DropColumn(
                name: "UsageDisk",
                table: "ManagerBOTs");

            migrationBuilder.UpdateData(
                table: "AppRoles",
                keyColumn: "Id",
                keyValue: "c1105ce5-9dbc-49a9-a7d5-c963b6daa62a",
                column: "ConcurrencyStamp",
                value: "2c6254ce-d19a-4e03-9ec6-4dd1921201bb");

            migrationBuilder.UpdateData(
                table: "AppUsers",
                keyColumn: "Id",
                keyValue: "ffded6b0-3769-4976-841b-69459049a62d",
                columns: new[] { "ConcurrencyStamp", "PasswordHash" },
                values: new object[] { "bfb48221-fd21-4440-a3eb-17a8778a3d5f", "AQAAAAEAACcQAAAAEFpYS6p1xQQCwNuAfIwJh7CDXYWKutANQIBmBylrxuhF0c9THUUPVyZrMAJPsmYlow==" });
        }
    }
}
