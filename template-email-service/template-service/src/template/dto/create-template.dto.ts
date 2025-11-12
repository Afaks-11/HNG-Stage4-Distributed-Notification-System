import { IsString, IsNotEmpty, IsOptional, IsBoolean } from 'class-validator';

export class CreateTemplateDto {
  @IsString()
  @IsNotEmpty()
  code: string; // Unique template code (e.g., 'welcome_email')

  @IsString()
  @IsNotEmpty()
  name: string; // Human-readable name

  @IsString()
  @IsNotEmpty()
  subject: string; // Email subject with {{variables}}

  @IsString()
  @IsNotEmpty()
  body: string; // HTML body with {{variables}}

  @IsBoolean()
  @IsOptional()
  is_active?: boolean; // Default: true
}
