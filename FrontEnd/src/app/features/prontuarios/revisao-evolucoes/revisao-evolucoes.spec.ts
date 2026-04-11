import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RevisaoEvolucoes } from './revisao-evolucoes';

describe('RevisaoEvolucoes', () => {
    let component: RevisaoEvolucoes;
    let fixture: ComponentFixture<RevisaoEvolucoes>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [RevisaoEvolucoes],
        }).compileComponents();

        fixture = TestBed.createComponent(RevisaoEvolucoes);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
