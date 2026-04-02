import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VisaoProntuario } from './visao-prontuario';

describe('VisaoProntuario', () => {
    let component: VisaoProntuario;
    let fixture: ComponentFixture<VisaoProntuario>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [VisaoProntuario],
        }).compileComponents();

        fixture = TestBed.createComponent(VisaoProntuario);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
