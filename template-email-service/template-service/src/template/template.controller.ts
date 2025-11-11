import { Controller, Get, Post, Put, Delete, Body, Param, Query } from '@nestjs/common';
import { TemplateService } from './template.service';
import { CreateTemplateDto } from './dto/create-template.dto';
import { UpdateTemplateDto } from './dto/update-template.dto';

@Controller('api/v1/templates')
export class TemplateController {
  constructor(private readonly templateService: TemplateService) {}

  @Post()
  async create(@Body() createTemplateDto: CreateTemplateDto) {
    const data = await this.templateService.create(createTemplateDto);
    return {
      success: true,
      message: 'Template created successfully',
      data,
    };
  }

  @Get()
  async findAll(@Query('page') page: number = 1, @Query('limit') limit: number = 10) {
    const result = await this.templateService.findAll(page, limit);
    return {
      success: true,
      message: 'Templates retrieved successfully',
      ...result,
    };
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    const data = await this.templateService.findOne(id);
    return {
      success: true,
      message: 'Template retrieved successfully',
      data,
    };
  }

  @Get('by-code/:code')
  async findByCode(@Param('code') code: string) {
    const data = await this.templateService.findByCode(code);
    return {
      success: true,
      message: 'Template retrieved successfully',
      data,
    };
  }

  @Get('by-name/:name')
  async findByName(@Param('name') name: string) {
    const data = await this.templateService.findByName(name);
    return {
      success: true,
      message: 'Templates retrieved successfully',
      data,
    };
  }

  @Put(':id')
  async update(@Param('id') id: string, @Body() updateTemplateDto: UpdateTemplateDto) {
    const data = await this.templateService.update(id, updateTemplateDto);
    return {
      success: true,
      message: 'Template updated successfully',
      data,
    };
  }

  @Delete(':id')
  async remove(@Param('id') id: string) {
    await this.templateService.remove(id);
    return {
      success: true,
      message: 'Template deleted successfully',
    };
  }

  @Get('history/:code')
  async getVersionHistory(@Param('code') code: string) {
    const data = await this.templateService.getVersionHistory(code);
    return {
      success: true,
      message: 'Version history retrieved successfully',
      data,
    };
  }
}
