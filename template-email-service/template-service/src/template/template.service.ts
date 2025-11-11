import { Injectable, NotFoundException, ConflictException } from '@nestjs/common';
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

  async findAll(page: number = 1, limit: number = 10): Promise<{ data: Template[]; total: number }> {
    const [data, total] = await this.templateRepository.findAndCount({
      skip: (page - 1) * limit,
      take: limit,
      order: { created_at: 'DESC' },
    });

    return { data, total };
  }

  async findOne(id: string): Promise<Template> {
    const template = await this.templateRepository.findOne({ where: { id } });
    if (!template) {
      throw new NotFoundException(`Template with ID "${id}" not found`);
    }
    return template;
  }

  async findByCode(code: string): Promise<Template> {
    const template = await this.templateRepository.findOne({ where: { code } });
    if (!template) {
      throw new NotFoundException(`Template with code "${code}" not found`);
    }
    return template;
  }

  async findByName(name: string): Promise<Template[]> {
    return await this.templateRepository.find({
      where: { name },
      order: { version: 'DESC' },
    });
  }

  async update(id: string, updateTemplateDto: UpdateTemplateDto): Promise<Template> {
    const template = await this.findOne(id);

    if (updateTemplateDto.subject || updateTemplateDto.body) {
      template.version += 1;
    }

    Object.assign(template, updateTemplateDto);
    return await this.templateRepository.save(template);
  }

  async remove(id: string): Promise<void> {
    const template = await this.findOne(id);
    await this.templateRepository.remove(template);
  }

  async getVersionHistory(code: string): Promise<Template[]> {
    return await this.templateRepository.find({
      where: { code },
      order: { version: 'DESC' },
    });
  }
}
