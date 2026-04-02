import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InsercaoEvolucao } from './insercao-evolucao';

describe('InsercaoEvolucao', () => {
    let component: InsercaoEvolucao;
    let fixture: ComponentFixture<InsercaoEvolucao>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [InsercaoEvolucao],
        }).compileComponents();

        fixture = TestBed.createComponent(InsercaoEvolucao);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
