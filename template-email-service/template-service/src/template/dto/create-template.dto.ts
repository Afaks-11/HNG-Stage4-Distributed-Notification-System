import { IsString, IsNotEmpty, IsOptional, Length } from 'class-validator';

export class CreateTemplateDto {
  @IsString()
  @IsNotEmpty()
  @Length(1, 100)
  code: string;

  @IsString()
  @IsNotEmpty()
  @Length(1, 255)
  name: string;

  @IsString()
  @IsNotEmpty()
  subject: string;

  @IsString()
  @IsNotEmpty()
  body: string;

  @IsString()
  @IsOptional()
  @Length(2, 10)
  language?: string;
}
