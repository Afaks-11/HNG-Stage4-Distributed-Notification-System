import { IsString, IsOptional, IsBoolean, Length } from 'class-validator';

export class UpdateTemplateDto {
  @IsString()
  @IsOptional()
  @Length(1, 255)
  name?: string;

  @IsString()
  @IsOptional()
  subject?: string;

  @IsString()
  @IsOptional()
  body?: string;

  @IsString()
  @IsOptional()
  @Length(2, 10)
  language?: string;

  @IsBoolean()
  @IsOptional()
  is_active?: boolean;
}
