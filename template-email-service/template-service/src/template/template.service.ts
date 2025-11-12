import { Injectable, NotFoundException, ConflictException, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Template } from './template.entity';
import { CreateTemplateDto } from './dto/create-template.dto';
import { UpdateTemplateDto } from './dto/update-template.dto';

@Injectable()
export class TemplateService {
  constructor(
    @InjectRepository(Template)
    private templateRepository: Repository<Template>,
  ) {}

  // Create a new template
  async create(createTemplateDto: CreateTemplateDto): Promise<Template> {
    const existing = await this.templateRepository.findOne({
      where: { code: createTemplateDto.code },
    });

    if (existing) {
      throw new ConflictException(`Template with code "${createTemplateDto.code}" already exists`);
    }

    const template = this.templateRepository.create(createTemplateDto);
    return await this.templateRepository.save(template);
  }

  // Get all templates (paginated)
  async findAll(page: number = 1, limit: number = 10): Promise<{ data: Template[]; total: number }> {
    const [data, total] = await this.templateRepository.findAndCount({
      where: { is_active: true },
      skip: (page - 1) * limit,
      take: limit,
      order: { created_at: 'DESC' },
    });

    return { data, total };
  }

  // Get template by ID
  async findOne(id: string): Promise<Template> {
    const template = await this.templateRepository.findOne({ where: { id } });
    if (!template) {
      throw new NotFoundException(`Template with ID "${id}" not found`);
    }
    return template;
  }

  // Get template by code (used by Email Service)
  async findByCode(code: string): Promise<Template> {
    const template = await this.templateRepository.findOne({ 
      where: { code, is_active: true } 
    });
    if (!template) {
      throw new NotFoundException(`Template with code "${code}" not found`);
    }
    return template;
  }

  // Render template with variables
  async renderTemplate(code: string, variables: Record<string, any>): Promise<{ subject: string; body: string }> {
    const template = await this.findByCode(code);

    const subject = this.replaceVariables(template.subject, variables);
    const body = this.replaceVariables(template.body, variables);

    return { subject, body };
  }

  // Simple variable replacement ({{variable}})
  private replaceVariables(text: string, variables: Record<string, any>): string {
    return text.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      return variables[key] !== undefined ? String(variables[key]) : match;
    });
  }

  // Update template
  async update(id: string, updateTemplateDto: UpdateTemplateDto): Promise<Template> {
    const template = await this.findOne(id);
    Object.assign(template, updateTemplateDto);
    return await this.templateRepository.save(template);
  }

  // Soft delete (set is_active = false)
  async remove(id: string): Promise<void> {
    const template = await this.findOne(id);
    template.is_active = false;
    await this.templateRepository.save(template);
  }
}
