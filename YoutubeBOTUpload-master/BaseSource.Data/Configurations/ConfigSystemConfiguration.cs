using BaseSource.Data.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace BaseSource.Data.Configurations
{
    public class ConfigSystemConfiguration : IEntityTypeConfiguration<ConfigSystem>
    {
        public void Configure(EntityTypeBuilder<ConfigSystem> builder)
        {
            builder.ToTable("ConfigSystems");

            builder.HasKey(x => x.Id);
            builder.Property(x => x.BankNumber).HasMaxLength(50);
            builder.Property(x => x.BankName).HasMaxLength(50);
            builder.Property(x => x.BankAccountName).HasMaxLength(50);
            builder.Property(x => x.LinkFBAdmin).HasMaxLength(500);
            builder.Property(x => x.LinkYoutube).HasMaxLength(500);
        }
    }
}
