import { Controller, Get, Post, Put, Delete, Body, Param, Query } from '@nestjs/common';
import { TemplateService } from './template.service';
import { CreateTemplateDto } from './dto/create-template.dto';
import { UpdateTemplateDto } from './dto/update-template.dto';

@Controller('api/v1/templates')
export class TemplateController {
  constructor(private readonly templateService: TemplateService) {}

  // Create new template
  @Post()
  async create(@Body() createTemplateDto: CreateTemplateDto) {
    const data = await this.templateService.create(createTemplateDto);
    return {
      success: true,
      message: 'Template created successfully',
      data,
    };
  }

  // Get all templates (paginated)
  @Get()
  async findAll(@Query('page') page: number = 1, @Query('limit') limit: number = 10) {
    const result = await this.templateService.findAll(page, limit);
    return {
      success: true,
      message: 'Templates retrieved successfully',
      ...result,
    };
  }

  // Get template by ID
  @Get(':id')
  async findOne(@Param('id') id: string) {
    const data = await this.templateService.findOne(id);
    return {
      success: true,
      message: 'Template retrieved successfully',
      data,
    };
  }

  // Get template by code (used by Email Service)
  @Get('by-code/:code')
  async findByCode(@Param('code') code: string) {
    const data = await this.templateService.findByCode(code);
    return {
      success: true,
      message: 'Template retrieved successfully',
      data,
    };
  }

  // Render template with variables (used by Email Service)
  @Post('render/:code')
  async renderTemplate(
    @Param('code') code: string,
    @Body() variables: Record<string, any>,
  ) {
    const data = await this.templateService.renderTemplate(code, variables);
    return {
      success: true,
      message: 'Template rendered successfully',
      data,
    };
  }

  // Update template
  @Put(':id')
  async update(@Param('id') id: string, @Body() updateTemplateDto: UpdateTemplateDto) {
    const data = await this.templateService.update(id, updateTemplateDto);
    return {
      success: true,
      message: 'Template updated successfully',
      data,
    };
  }

  // Delete template (soft delete)
  @Delete(':id')
  async remove(@Param('id') id: string) {
    await this.templateService.remove(id);
    return {
      success: true,
      message: 'Template deleted successfully',
    };
  }
}
