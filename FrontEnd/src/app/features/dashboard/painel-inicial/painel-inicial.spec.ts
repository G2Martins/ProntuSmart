import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PainelInicial } from './painel-inicial';

describe('PainelInicial', () => {
    let component: PainelInicial;
    let fixture: ComponentFixture<PainelInicial>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [PainelInicial],
        }).compileComponents();

        fixture = TestBed.createComponent(PainelInicial);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
